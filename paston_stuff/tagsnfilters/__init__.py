def parse_templatetagtoken(token):
    # Return a dictionary of arguments passed to the tag
    # TODO:
    # This is fubarred: will break if there are commas in values
    import string
    kwargs={}
    # Strip off the tag name:
    arg_string=token.contents.strip().lstrip(string.letters+string.digits+'_').strip()

    if arg_string:
        if ',' not in arg_string:
            # ensure at least one ','
            arg_string += ','
        for arg in arg_string.split(','):
            arg = arg.strip()
            if arg:
                kw, val = arg.split('=', 1)
                kw = kw.lower()
                # TO DO: This is wrong - will strip multiple 's
                kwargs[kw] = val.strip().strip('"\'')
    return kwargs
