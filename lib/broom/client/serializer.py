import broom
import json

class BroomObjectSerializer(object):
    """A simple serializer for exporting an object to JSON
    and reinstantiating it from JSON, with a subsequent
    database merge.

    """
    @classmethod
    def serialize(cls, obj):
        return json.dumps(obj.toDict(meta=True))

    @classmethod
    def deserialize(cls, data):
        data = json.loads(data)
        meta = data.pop('broom:meta', {})
        object_type = meta.get('object_type')
        if not object_type:
            raise RuntimeError("Not enough details to deserialize; you need "
                               "to include broom:meta and its object_type "
                               "entry.")
        object_type = broom.types.get(object_type)

        # If any primary key is specified, they all need to 
        # be specified.
        ks = [c.name for c in broom.inspect(object_type).primary_key]
        vs = [data.get(k) for k in keys]
        if any(vs) and not all(vs):
            raise RuntimeError("You must either specify either all key "
                               "columns or none.")
        kwargs = {}
        for c in broom.inspect(object_type).columns.keys():
            if c not in data:
                continue
            kwargs[c] = data.pop(c)
        if data:
            raise RuntimeError("Invalid field(s) specified for object.")
        obj = object_type(**kwargs)
        if obj.pk and obj.pk[0] is not None:
            obj = broom.db._merge(obj)
        return obj
