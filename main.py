import random

import uvicorn
from fastapi import FastAPI, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise

from config import DB_URL
from models import Group, Group_Pydantic, GroupIn_Pydantic, GroupList_Pydantic, \
    Participant_Pydantic, ParticipantIn_Pydantic, Participant

app = FastAPI()


@app.post("/group", response_model=int)
async def create_group(group: GroupIn_Pydantic):
    saved_group = await Group(**group.dict())
    await saved_group.save()
    return saved_group.id


@app.get("/groups", response_model=list[GroupList_Pydantic])
async def get_groups():
    groups = Group.all()
    return await GroupList_Pydantic.from_queryset(groups)


@app.get("/group/{group_id}", response_model=Group_Pydantic)
async def get_group(group_id: int):
    group = Group.get(id=group_id)
    return await Group_Pydantic.from_queryset_single(group)


@app.put("/group/{group_id}", response_model=Group_Pydantic)
async def update_group(group_id: int, group: GroupIn_Pydantic):
    saved_group = await Group.get(id=group_id)
    await saved_group.update_from_dict(group.dict())
    return await Group_Pydantic.from_tortoise_orm(saved_group)


@app.delete("/group/{group_id}", response_model=Group_Pydantic)
async def delete_group(group_id: int):
    deleted_group = await Group.get(id=group_id)
    await deleted_group.delete()
    return await Group_Pydantic.from_tortoise_orm(deleted_group)


@app.post("/group/{group_id}/participant", response_model=int)
async def create_participant(group_id: int, participant: ParticipantIn_Pydantic):
    group = await Group.get(id=group_id)
    saved_participant = await Participant(**participant.dict())
    await saved_participant.save()
    await group.participants.add(saved_participant)
    return saved_participant.id


@app.delete("/group/{group_id}/participant/{participant_id}", response_model=Participant_Pydantic)
async def delete_participant(group_id: int, participant_id: int):
    group = await Group.get(id=group_id)
    saved_participant = await Participant.get(id=participant_id)
    await group.participants.remove(saved_participant)
    await saved_participant.delete()
    return await Participant_Pydantic.from_tortoise_orm(saved_participant)


@app.post("/group/{group_id}/toss", response_model=list[Participant_Pydantic], responses={
    status.HTTP_409_CONFLICT: {
        "description": "Number of participants is less than 3"
    }
})
async def toss(group_id: int):
    group = await Group.get(id=group_id).prefetch_related('participants')
    participants = list(group.participants)
    if len(participants) < 3:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough participants")
    random.shuffle(participants)

    for i in range(len(participants)):
        participant = participants[i]
        if i == len(participants) - 1:
            participant.recipient = participants[0]
        else:
            participant.recipient = participants[i + 1]

        await participant.save()

    return await Participant_Pydantic.from_queryset(group.participants.all())


@app.get("/group/{group_id}/participant/{participant_id}/recipient",
         response_model=Participant_Pydantic)
async def get_recipient(group_id: int, participant_id: int):
    group = await Group.get(id=group_id)
    participant = await group.participants.all().get(id=participant_id)
    return await Participant_Pydantic.from_queryset_single(participant.recipient)


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == '__main__':
    uvicorn.run(app, port=8080)
