# Imports
import string

VALID_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
def slugify_filename(filename):
    '''
    Input: Name of a file
    Output: Name with all dissallowed characters remove. This is not perfect. For instance, will fail to detect "CON"
    '''
    return ''.join(c for c in filename if c in VALID_CHARS)