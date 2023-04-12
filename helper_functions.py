import os
#from TkAlExceptions import AllInOneError

####################--- Helpers ---############################
def replaceByMap(target, the_map):
    """This function replaces `.oO[key]Oo.` by `the_map[key]` in target.

    Arguments:
    - `target`: String which contains symbolic tags of the form `.oO[key]Oo.`
    - `the_map`: Dictionary which has to contain the `key`s in `target` as keys
    """

    result = target
    for key in the_map:
        lifeSaver = 10e3
        iteration = 0
        while ".oO[" in result and "]Oo." in result:
            for key in the_map:
                result = result.replace(".oO["+key+"]Oo.",the_map[key])
                iteration += 1
            if iteration > lifeSaver:
                problematicLines = ""
                for line in result.splitlines():
                    if  ".oO[" in result and "]Oo." in line:
                        problematicLines += "%s\n"%line
                msg = ("Oh Dear, there seems to be an endless loop in "
                       "replaceByMap!!\n%s\nrepMap"%problematicLines)
                #raise AllInOneError(msg)
    return result

