# coding=UTF-8
import scrypt
import hashlib
import hmac

_ENCODING = 'utf-8'
_BYTE_ORDER = 'big'
_INT_BYTES = 4


def masterKey(master_password, name):
    """Phase 1: Your identity

    Your identity is defined by your master key.  This key unlocks all of your
    doors.  Your master key is the cryptographic result of two components:

    1.Your <name> (identification)
    2.Your <master password> (authentication)

    Your master password is your personal secret and your name scopes that
    secret to your identity.  Together, they create a cryptographic identifier
    that is unique to your person.

    ´´´
    masterKey = SCRYPT( key, seed, N, r, p, dkLen )
    key = <master password>
    seed = scope . LEN(<name>) . <name>
    N = 32768
    r = 8
    p = 2
    dkLen = 64
    ´´´

    We employ the SCRYPT cryptographic function to derive a 64-byte
    cryptographic key from the user’s name and master password using a fixed
    set of parameters.

    """
    key = master_password.encode(_ENCODING)
    length_name_as_bytes = len(name.encode(_ENCODING)).to_bytes(
        length=_INT_BYTES,
        byteorder=_BYTE_ORDER,
        signed=False)
    seed = 'com.lyndir.masterpassword'.encode(_ENCODING) + \
        length_name_as_bytes + name.encode(_ENCODING)
    N = 32768
    r = 8
    p = 2
    dkLen = 64
    return scrypt.hash(key, seed, N, r, p, dkLen)


def sitekey(site_name, master_key, counter):
    """Phase 2: Your site key "com.lyndir.masterpassword"

    Your site key is a derivative from your master key when it is used to
    unlock the door to a specific site. Your site key is the result of two
    components:

    1.Your <site name> (identification)
    2.Your <masterkey> (authentication)
    3.Your <site counter>

    Your master key ensures only your identity has access to this key and your
    site name scopes the key to your site.  The site counter ensures you can
    easily create new keys for the site should a key become
    compromised. Together, they create a cryptographic identifier that is
    unique to your account at this site.

    siteKey = HMAC-SHA-256( key, seed )
    key = <master key>
    seed = scope . LEN(<site name>) . <site name> . <counter>

    We employ the HMAC-SHA-256 cryptographic function to derive a 64-byte
    cryptographic site key from the from the site name and master key scoped
    to a given counter value.
    """
    key = master_key
    length_site_name_as_bytes = len(site_name.encode(_ENCODING)).to_bytes(
        length=_INT_BYTES,
        byteorder=_BYTE_ORDER,
        signed=False)
    counter_as_bytes = counter.to_bytes(length=_INT_BYTES,
                                        byteorder=_BYTE_ORDER,
                                        signed=False)
    seed = 'com.lyndir.masterpassword'.encode(_ENCODING) + \
        length_site_name_as_bytes + site_name.encode(_ENCODING) + \
        counter_as_bytes
    return hmac.new(key, seed, hashlib.sha256).digest()


""" Output Templates:
 In an effort to enforce increased password entropy, a common consensus has
 developed among account administrators that passwords should adhere to
 certain arbitrary password policies.  These policies enforce certain rules
 which must be honoured for an account password to be deemed acceptable.

 As a result of these enforcement practices, Master Password’s site key
 output must necessarily adhere to these types of policies.  Since password
 policies are governed by site administrators and not standardized, Master
 Password defines several password templates to make a best-effort attempt at
 generating site passwords that conform to these policies while also keeping
 its output entropy as high as possible under the constraints.
"""
template_dictionary = {
    'Maximum': ['anoxxxxxxxxxxxxxxxxx', 'axxxxxxxxxxxxxxxxxno'],
    'Long': ['CvcvnoCvcvCvcv',
             'CvcvCvcvnoCvcv',
             'CvcvCvcvCvcvno',
             'CvccnoCvcvCvcv',
             'CvccCvcvnoCvcv',
             'CvccCvcvCvcvno',
             'CvcvnoCvccCvcv',
             'CvcvCvccnoCvcv',
             'CvcvCvccCvcvno',
             'CvcvnoCvcvCvcc',
             'CvcvCvcvnoCvcc',
             'CvcvCvcvCvccno',
             'CvccnoCvccCvcv',
             'CvccCvccnoCvcv',
             'CvccCvccCvcvno',
             'CvcvnoCvccCvcc',
             'CvcvCvccnoCvcc',
             'CvcvCvccCvccno',
             'CvccnoCvcvCvcc',
             'CvccCvcvnoCvcc',
             'CvccCvcvCvccno'],
    'Medium': ['CvcnoCvc', 'CvcCvcno'],
    'Short': ['Cvcn'],
    'Basic': ['aaanaaan', 'aannaaan', 'aaannaaa'],
    'PIN': ['nnnn'],
    'Name': ['cvccvcvcv'],
    'Phrase': ['cvcc cvc cvccvcv cvc',
               'cvc cvccvcvcv cvcv',
               'cv cvccv cvc cvcvccv']
    }
# Master Password Character Classes

# A Master Password template is a string of characters, where each character
# identifies a certain character class.  As such, the template specifies that
# the output password should be formed by substituting each of the template’s
# character class characters by a chosen character from that character class.
template_chars_dictionary = {
    'V': list('AEIOU'),
    'C': list('BCDFGHJKLMNPQRSTVWXYZ'),
    'v': list('aeiou'),
    'c': list('bcdfghjklmnpqrstvwxyz'),
    'A': list('AEIOUBCDFGHJKLMNPQRSTVWXYZ'),
    'a': list('AEIOUaeiouBCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz'),
    'n': list('0123456789'),
    'o': list("""@&%?,=[]_:-+*$#!'^~;()/."""),
    'x': list("""AEIOUaeiouBCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz0123456789!@#$%^&*()"""),
    ' ': list(" ")
}


def password(site_key, template_class):
    """Phase 3: Your site password

    Your site password is an identifier derived from your site key in
    compoliance with the site’s password policy.

    The purpose of this step is to render the site’s cryptographic key into a
    format that the site’s password input will accept.

    Master Password declares several site password formats and uses these
    pre-defined password “templates” to render the site key legible.

    ´´´
    template = templates[ <site key>[0] % LEN( templates ) ]

    for i in 0..LEN( template )
      passChars = templateChars[ template[i] ]2
      passWord[i] = passChars[ <site key>[i+1] % LEN( passChars ) ]

    We resolve a template to use for the password from the site key’s first
    byte.  As we iterate the template, we use it to translate site key bytes
    into password characters.  The result is a site password in the form
    defined by the site template scoped to our site key.

    This password is then used to authenticate the user for his account at
    this site."""

    if template_class not in template_dictionary:
        raise ValueError("%s not a valid template" % template_class)
    templates = template_dictionary[template_class]
    template = templates[site_key[0] % len(templates)]
    password = []
    for i in range(len(template)):
        pass_chars = template_chars_dictionary[template[i]]
        password.append(pass_chars[site_key[i+1] % len(pass_chars)])
    return ''.join(password)


def generate_password(full_name,
                      master_password,
                      site_name,
                      site_counter,
                      result_type):
    master_key = masterKey(master_password,
                           full_name)
    site_key = sitekey(site_name,
                       master_key,
                       site_counter)
    return password(site_key, result_type)


left_arm_list = ["╔", "╚", "╰", "═"]
right_arm_list = ["╗", "╝", "╯", "═"]
body_list = ["█", "░", "▒", "▓", "☺", "☻"]
accessory_list = [
    "◈", "◎", "◐", "◑", "◒", "◓", "☀", "☁", "☂", "☃", "", "★",
    "☆", "☎", "☏", "⎈", "⌂", "☘", "☢", "☣", "☕", "⌚", "⌛", "⏰",
    "⚡", "⛄", "⛅", "☔", "♔", "♕", "♖", "♗", "♘", "♙", "♚", "♛",
    "♜", "♝", "♞", "♟", "♨", "♩", "♪", "♫", "⚐", "⚑", "⚔", "⚖",
    "⚙", "⚠", "⌘", "⏎", "✄", "✆", "✈", "✉", "✌"]
color_code = {"Red": '\033[31m', "Green": '\033[32m', "Yellow":
              '\033[33m', "Blue": '\033[34m', "Magenta": '\033[35m',
              "Cyan": '\033[36m', "White": '\033[37m'}
color_list = ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]


def identicon(full_name, master_password, use_color=False):
    non_legit_input = ((len(full_name) == 0) or (full_name is None) or
                       (len(master_password) == 0) or master_password is None)
    if non_legit_input:
        return ""
    seed = hmac.new(master_password.encode(_ENCODING),
                    full_name.encode(_ENCODING),
                    hashlib.sha256).digest()
    left_arm = left_arm_list[seed[0] % len(left_arm_list)]
    body = body_list[seed[1] % len(body_list)]
    right_arm = right_arm_list[seed[2] % len(right_arm_list)]
    accessory = accessory_list[seed[3] % len(accessory_list)]
    color = color_list[seed[4] % len(color_list)]
    icon = "%s%s%s%s" % (left_arm, body, right_arm, accessory)
    if use_color:
        return color_code[color] + icon + color_code["White"]
    else:
        return icon
