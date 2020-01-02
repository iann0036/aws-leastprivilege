class BasePermissions:
    def _get_property_or_default(self, res, notfoundvalue, *propertypath):
        value = '*'

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue

            if isinstance(relpath, str):  # TODO: Other primitive types
                value = relpath
            elif isinstance(relpath, list):
                for listitem in relpath:
                    if not isinstance(listitem, str):
                        return value
                value = relpath

        return value

    def _get_property_array_length(self, res, notfoundvalue, *propertypath):
        value = 0

        if "Properties" in res:
            relpath = res["Properties"]
            for pathpart in propertypath:
                if pathpart in relpath:
                    relpath = relpath[pathpart]
                else:
                    return notfoundvalue

            if isinstance(relpath, list):
                value = len(relpath)

        return value
