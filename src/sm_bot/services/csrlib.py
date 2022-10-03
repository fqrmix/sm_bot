import pathlib
from sm_bot.services.logger import logger

def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')

    if isinstance(data, dict):
        return dict(map(convert, data.items()))

    if isinstance(data, tuple):
        return map(convert, data)

    return data

def csr_validation(csr_file, file_info):
    if not file_info.file_path.endswith('.csr'):
        raise Exception(f'У файла, который ты прислал, расширение не .CSR,'\
                        f'а "{pathlib.Path(file_info.file_path).suffix}"'
        )
    else:
        logger.info('[csr-decoder] .csr file found!')
        strFile = convert(csr_file).splitlines()
        if not strFile[0] == "-----BEGIN CERTIFICATE REQUEST-----":
            raise Exception(f'Начало запроса на сертификат некорректно!\n{strFile[0]}')
        else:
            logger.info('[csr-decoder] Start of CSR is OK')
            if not strFile[len(strFile) - 1] == "-----END CERTIFICATE REQUEST-----":
                raise Exception(f'Окончание запроса на сертификат некорректно!\n{strFile[len(strFile) - 1]}')
            else:
                logger.info('[csr-decoder] End of CSR is OK')
                return True