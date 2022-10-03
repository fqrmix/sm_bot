import OpenSSL.crypto
from OpenSSL.crypto import load_certificate_request, FILETYPE_PEM
from sm_bot.services.csrlib import convert, csr_validation
from sm_bot.services.logger import logger
from telebot import TeleBot, types

def handle_csr_request(message: types.Message, bot: TeleBot):
    try:
        logger.info(f'[csr-decoder] User {message.from_user.id} start CSR decoder')
        chat_id = message.chat.id
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        logger.info('[csr-decoder] Checking CSR...')

        if csr_validation(downloaded_file, file_info):
            req = load_certificate_request(FILETYPE_PEM, downloaded_file)
            key = req.get_pubkey()
            key_type = 'RSA' if key.type() == OpenSSL.crypto.TYPE_RSA else 'DSA'
            subject = req.get_subject()
            components = dict(subject.get_components())
            str_components = convert(components)
            bot.reply_to(message, f"Common name: {str_components ['CN']}\n"
                                  f"Organisation: {str_components ['O']}\n"
                                  f"State/province: {str_components ['ST']}\n"
                                  f"Country: {str_components ['C']}\n"
                                  f"Key algorithm: {key_type}\n"
                                  f"Key size: {key.bits()}"
            )
            cert_str = convert(downloaded_file)
            inline_cert_str = '`' + cert_str + '`'
            bot.send_message(chat_id, inline_cert_str, parse_mode='Markdown')
            logger.info('[csr-decoder] CSR decoding was successfull!')
    except Exception as e:
        bot.reply_to(message, e)
        logger.error(f'[csr-decoder] {e}')

