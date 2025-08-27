from fastapi import APIRouter
from src.ab.db.session import get_conn
from src.ab.schemas.experiments import ExperimentIn, ExperimentOut
import json


router = APIRouter(prefix="/experiments", tags=["Experiments"])


{
  "experiment_name": "button_color",
  "source": "alifshop",
  "groups": [
    { "group": 1, "ratio": 50, "params": { "color": "red", "text": "Купить через красную кнопку" } },
    { "group": 2, "ratio": 50, "params": { "color": "blue", "text": "Купить через синюю кнопку" } }
  ]
}


# @router.post("/", response_model=ExperimentOut)
# def create_experiment(payload: ExperimentIn):
#     with get_conn() as conn, conn.cursor() as cur:
#         cur.execute("""
#             insert into "a-b".experiments(experiment_name, source, groups_count)
#             values (%s, %s, %s)
#             returning experiment_id, experiment_name, source, groups_count
#         """, (payload.experiment_name, payload.source, len(payload.groups)))
#         exp_id, name, source, groups_count = cur.fetchone()

#         for g in payload.groups:
#             cur.execute("""
#                 insert into "a-b".groups_ratio(experiment_id, "group", ratio)
#                 values (%s, %s, %s)
#             """, (exp_id, g.group, g.ratio))

#         conn.commit()

#     return ExperimentOut(
#         experiment_id=exp_id,
#         experiment_name=name,
#         source=source,
#         groups_count=groups_count
#     )


@router.post("/", response_model=ExperimentOut)
def create_experiment(payload: ExperimentIn):
    with get_conn() as conn, conn.cursor() as cur:
        # создаём эксперимент
        cur.execute("""
            insert into "a-b".experiments(experiment_name, source, groups_count)
            values (%s, %s, %s)
            returning experiment_id, experiment_name, source, groups_count
        """, (payload.experiment_name, payload.source, len(payload.groups)))
        exp_id, name, source, groups_count = cur.fetchone()

        # сохраняем группы с параметрами
        for g in payload.groups:
            cur.execute("""
                insert into "a-b".groups_ratio(experiment_id, "group", ratio, params)
                values (%s, %s, %s, %s::jsonb)
            """, (exp_id, g.group, g.ratio, json.dumps(g.params)))

        conn.commit()

    return ExperimentOut(
        experiment_id=exp_id,
        experiment_name=name,
        source=source,
        groups_count=groups_count
    )
