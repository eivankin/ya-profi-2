from tortoise.fields import ManyToManyField
from tortoise.models import Model
from tortoise import fields, Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator


class Participant(Model):
    name = fields.CharField(max_length=255)
    wish = fields.CharField(max_length=255)

    recipient = fields.ForeignKeyField('models.Participant', null=True, related_name=False)


class Group(Model):
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255, null=True)

    participants = ManyToManyField('models.Participant')


Tortoise.init_models(["models"], "models")
ParticipantIn_Pydantic = pydantic_model_creator(Participant, name='ParticipantIn',
                                                exclude_readonly=True, exclude=('recipient',))
_Participant_Pydantic = pydantic_model_creator(Participant, name='Participant', exclude=('groups',))
Recipient_Pydantic = pydantic_model_creator(Participant, name='Recipient',
                                            exclude=('groups', 'recipient', 'recipient_id'))


class Participant_Pydantic(_Participant_Pydantic):
    recipient: Recipient_Pydantic


GroupIn_Pydantic = pydantic_model_creator(Group, name='GroupIn', exclude_readonly=True)
GroupList_Pydantic = pydantic_model_creator(Group, name='GroupList', exclude=('participants',))
Group_Pydantic = pydantic_model_creator(Group, name='Group')
