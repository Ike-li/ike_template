from marshmallow import Schema, fields, validate


class PersonSerializer(Schema):

    class Meta:
        fields = ("first_name", "last_name")


class FirstNameValidator(Schema):
    first_name = fields.Str(
        required=True, validate=[validate.Length(min=1, max=20)]
    )


class PersonValidator(FirstNameValidator):
    last_name = fields.Str(
        required=True, validate=[validate.Length(min=1, max=20)]
    )
