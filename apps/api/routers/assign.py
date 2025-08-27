from fastapi import APIRouter, Query, HTTPException
from src.ab.db.session import get_conn
import hashlib
import random

router = APIRouter(prefix="/assign", tags=["Assign"])


def choose_group(user_id: str, ratios: list[tuple[int, int]]) -> int:
    """
    ratios: [(group, ratio), ...]
    Используем хеш, чтобы было sticky.
    """
    h = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
    r = h % 100
    acc = 0
    for g, ratio in ratios:
        acc += ratio
        if r < acc:
            return g
    return ratios[-1][0]  # fallback


# @router.get("/")
# def assign(experiment_id: int = Query(...), user_id: str = Query(...)):
#     with get_conn() as conn, conn.cursor() as cur:
#         # Проверяем, есть ли уже split
#         cur.execute("""
#             select "group" from "a-b".splits
#             where experiment_id=%s and user_id=%s
#         """, (experiment_id, user_id))
#         row = cur.fetchone()
#         if row:
#             return {"experiment_id": experiment_id, "user_id": user_id, "group": row[0]}

#         # Берем конфигурацию групп
#         cur.execute("""
#             select "group", ratio from "a-b".groups_ratio
#             where experiment_id=%s
#             order by "group"
#         """, (experiment_id,))
#         ratios = cur.fetchall()
#         if not ratios:
#             raise HTTPException(
#                 404, "experiment not found or no groups configured")

#         # Выбираем группу
#         group = choose_group(user_id, ratios)

#         # Сохраняем split
#         cur.execute("""
#             insert into "a-b".splits(experiment_id, "group", user_id)
#             values (%s, %s, %s)
#             returning split_id
#         """, (experiment_id, group, user_id))
#         split_id = cur.fetchone()[0]
#         conn.commit()

#     return {
#         "experiment_id": experiment_id,
#         "user_id": user_id,
#         "group": group,
#         "split_id": split_id
#     }


@router.get("/")
def assign(experiment_id: int = Query(...), user_id: str = Query(...)):
    with get_conn() as conn, conn.cursor() as cur:
        # Проверяем, есть ли уже split
        cur.execute("""
            select s."group", e.experiment_name, gr.ratio, gr.params
            from "a-b".splits s
            join "a-b".experiments e on e.experiment_id = s.experiment_id
            join "a-b".groups_ratio gr 
                 on gr.experiment_id = s.experiment_id and gr."group" = s."group"
            where s.experiment_id=%s and s.user_id=%s
        """, (experiment_id, user_id))
        row = cur.fetchone()
        if row:
            group, exp_name, ratio, params = row
            return {
                "experiment_id": experiment_id,
                "experiment_name": exp_name,
                "user_id": user_id,
                "group": group,
                "ratio": ratio,
                "params": params
            }

        # Берем конфигурацию групп
        cur.execute("""
            select "group", ratio, params 
            from "a-b".groups_ratio
            where experiment_id=%s
            order by "group"
        """, (experiment_id,))
        ratios = cur.fetchall()
        if not ratios:
            raise HTTPException(404, "experiment not found or no groups configured")

        # Выбираем группу
        group = choose_group(user_id, [(g, r) for g, r, _ in ratios])

        # Сохраняем split
        cur.execute("""
            insert into "a-b".splits(experiment_id, "group", user_id)
            values (%s, %s, %s)
            returning split_id
        """, (experiment_id, group, user_id))
        split_id = cur.fetchone()[0]

        # Достаём инфу о группе и эксперименте
        cur.execute("""
            select e.experiment_name, gr.ratio, gr.params
            from "a-b".experiments e
            join "a-b".groups_ratio gr 
                 on gr.experiment_id = e.experiment_id and gr."group" = %s
            where e.experiment_id=%s
        """, (group, experiment_id))
        exp_name, ratio, params = cur.fetchone()

        conn.commit()

    return {
        "experiment_id": experiment_id,
        "experiment_name": exp_name,
        "user_id": user_id,
        "group": group,
        "split_id": split_id,
        "ratio": ratio,
        "params": params
    }
