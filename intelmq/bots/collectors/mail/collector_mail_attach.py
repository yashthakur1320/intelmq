# -*- coding: utf-8 -*-
"""
In Version 0.9.5 the attachment filename is no longer surrounded by double quotes, see for the discussion:
https://github.com/certtools/intelmq/pull/1134
https://github.com/martinrusev/imbox/commit/7c6cc2fb5f7e39c1496d68f3d432eec19517bf8e#diff-1ae09572064c2e7c225de54ad5b49154
"""
import re
import zipfile

from intelmq.lib.bot import CollectorBot

try:
    import imbox
except ImportError:
    imbox = None


class MailAttachCollectorBot(CollectorBot):

    def init(self):
        if imbox is None:
            self.logger.error('Could not import imbox. Please install it.')
            self.stop()

    def process(self):
        mailbox = imbox.Imbox(self.parameters.mail_host,
                              self.parameters.mail_user,
                              self.parameters.mail_password,
                              self.parameters.mail_ssl)
        emails = mailbox.messages(folder=self.parameters.folder, unread=True)

        if emails:
            for uid, message in emails:

                if (self.parameters.subject_regex and
                        not re.search(self.parameters.subject_regex,
                                      re.sub("\r\n\s", " ", message.subject))):
                    continue

                for attach in message.attachments:
                    if not attach:
                        continue

                    attach_filename = attach['filename']
                    if attach_filename.startswith('"'):  # for imbox versions older than 0.9.5, see also above
                        attach_filename = attach_filename[1:-1]

                    if re.search(self.parameters.attach_regex, attach_filename):

                        if self.parameters.attach_unzip:
                            zipped = zipfile.ZipFile(attach['content'])
                            raw_report = zipped.read(zipped.namelist()[0])
                        else:
                            raw_report = attach['content'].read()

                        report = self.new_report()
                        report.add("raw", raw_report)

                        self.send_message(report)

                        # Only mark read if message relevant to this instance,
                        # so other instances watching this mailbox will still
                        # check it.
                        mailbox.mark_seen(uid)
                self.logger.debug("Email report read.")
        mailbox.logout()


BOT = MailAttachCollectorBot
