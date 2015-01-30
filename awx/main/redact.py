import re
import urlparse

class UriCleaner(object):
    REPLACE_STR = '$encrypted$'
    # https://regex101.com/r/sV2dO2/2
    SENSITIVE_URI_PATTERN = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))', re.MULTILINE)

    @staticmethod
    def remove_sensitive(cleartext):
        redactedtext = cleartext
        text_index = 0
        while True:
            match = UriCleaner.SENSITIVE_URI_PATTERN.search(redactedtext, text_index)
            if not match:
                break
            o = urlparse.urlsplit(match.group(1))
            if not o.username and not o.password:
                flag_continue = False
                if o.netloc:
                    # Handle the special case url http://username:password that can appear in SCM url
                    # on account of a bug? in ansible redaction
                    try:
                        (username, password) = o.netloc.split(':')
                    except ValueError as e:
                        flag_continue = True
                        pass

                if flag_continue:
                    text_index += len(match.group(1))
                    continue
            else:
                username = o.username
                password = o.password


            # Given a python MatchObject, with respect to redactedtext, find and 
            # replace the first occurance of username and the first and second
            # occurance of password

            # TODO: Ideally, we would replace username and password using the index
            # that they were found at.
            uri_str = redactedtext[match.start():match.end()]
            if username:
                uri_str = uri_str.replace(username, UriCleaner.REPLACE_STR, 1)
            # 2, just in case the password is $encrypted$
            if password:
                uri_str = uri_str.replace(password, UriCleaner.REPLACE_STR, 2)

            t = redactedtext[:match.start()] + uri_str
            text_index = len(t)
            if (match.end() < len(redactedtext)):
                t += redactedtext[match.end():]

            redactedtext = t
            if text_index >= len(redactedtext):
                text_index = len(redactedtext) - 1

        return redactedtext


