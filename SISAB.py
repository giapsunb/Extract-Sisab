from typing import Iterable, Tuple, Union, Dict, TextIO
from collections.abc import Iterable as Iter
import requests as req
from bs4 import BeautifulSoup
from bs4.element import Tag


def must_set(*options):
    def wrapper(fun):
        def check(object, *args, **kwargs):
            if any(map(lambda o: len(object.__getattribute__(o)) == 0, options)):
                raise AssertionError(
                    'Os atributos ({}) não estão configurados'.format(', '.join(options)))
            return fun(object, *args, **kwargs)
        return check
    return wrapper


class Sisab:  # {{{
    HOST = "https://sisab.saude.gov.br"
    URL = HOST + "/paginas/acessoRestrito/relatorio/federal/indicadores/indicadorPainel.xhtml"

    def __init__(self):  # {{{
        super().__init__()
        self.__view_state__ = ''
        self.__last_request__ = ''
        self.__option_key__ = ''

        self.__area_options__: Dict[str, str] = dict()
        self.__national_options__: Dict[str, str] = dict()
        self.__region_options__: Dict[str, str] = dict()
        self.__state_options__: Dict[str, str] = dict()
        self.__municipality_options__: Dict[str, str] = dict()
        self.__index_options__: Dict[str, str] = dict()
        self.__period_options__: Dict[str, str] = dict()
        self.__view_options__: Dict[str, str] = dict()

        self.__index__ = ''  # Indicador
        self.__period__ = ''  # Período da pesquisa (precisa ser configurado)
        self.__view__ = ''  # Visão de equipe

        self.__area__: str = ''
        self.__region__: Union[str, Tuple[str, ...]] = ''
        self.__state__: Union[str, Tuple[str, ...]] = ''
        self.__municipality__: Union[str, Tuple[str, ...]] = ''

        self.__cookies__ = []
        self.__get_cookies__()

        self.post()
        soup = BeautifulSoup(self.__last_request__, 'html.parser')
        self.__area_options__ = {k: v for k, v in map(
            lambda o: (o.attrs['value'], o.get_text()),
            soup.select('select#selectLinha option')
        )}
        # }}}

    # {{{ Getters
    @property
    def area_options(self) -> Dict[str,
                                   str]: return self.__area_options__.copy()

    @property
    def national_options(
        self) -> Dict[str, str]: return self.__national_options__.copy()

    @property
    def region_options(
        self) -> Dict[str, str]: return self.__region_options__.copy()

    @property
    def state_options(self) -> Dict[str,
                                    str]: return self.__state_options__.copy()

    @property
    def municipality_options(
        self) -> Dict[str, str]: return self.__municipality_options__.copy()

    @property
    def index_options(self) -> Dict[str,
                                    str]: return self.__index_options__.copy()

    @property
    def period_options(
        self) -> Dict[str, str]: return self.__period_options__.copy()

    @property
    def view_options(self) -> Dict[str,
                                   str]: return self.__view_options__.copy()

    @property
    def area(self): return self.__area__
    @property
    def region(self): return self.__region__
    @property
    def state(self): return self.__state__
    @property
    def municipality(self): return self.__municipality__
    @property
    def index(self): return self.__index__
    @property
    def period(self): return self.__period__
    @property
    def view(self): return self.__view__
    # }}}
    # {{{ Setters

    @area.setter
    def area(self, value: Union[str, int]):
        if isinstance(value, str):
            if value not in self.area_options:
                raise ValueError('Valor inválido para área')
            self.__area__ = value
        elif isinstance(value, int):
            try:
                self.__area__ = list(self.area_options.keys())[value]
            except IndexError:
                raise IndexError('Indíce inválido para área')
        else:
            raise TypeError('Tipo inválido para área')

    @region.setter
    def region(self, value: Union[str, Iterable[str], Iterable[int]]):
        if isinstance(value, str):
            if value not in self.region_options:
                raise ValueError('Valor inválido para região')
            self.__region__ = value
        elif isinstance(value, Iter):
            if all(map(lambda v: type(v) == int, value)):
                try:
                    self.__region__ = tuple([k for i, k in enumerate(
                        self.region_options.keys()) if i in value])  # type: ignore
                except IndexError:
                    raise IndexError('Indíce inválido para região')
            else:
                if any(map(lambda o: o not in self.region_options, value)):
                    raise ValueError('Valor inválido para região')
                self.__region__ = tuple(value)  # type: ignore
        else:
            raise TypeError('Tipo inválido para região')

    @state.setter
    def state(self, value: Union[str, Iterable[str], Iterable[int]]):
        if isinstance(value, str):
            if value not in self.state_options:
                raise ValueError('Valor inválido para estado')
            self.__state__ = value
        elif isinstance(value, Iter):
            if all(map(lambda v: type(v) == int, value)):
                try:
                    self.__state__ = tuple([k for i, k in enumerate(
                        self.state_options.keys()) if i in value])  # type: ignore
                except IndexError:
                    raise IndexError('Indíce inválido para estado')
            else:
                if any(map(lambda o: o not in self.state_options, value)):
                    raise ValueError('Valor inválido para estado')
                self.__state__ = tuple(value)  # type: ignore
        else:
            raise TypeError('Tipo inválido para estado')

    @municipality.setter
    def municipality(self, value: Union[str, Iterable[str], Iterable[int]]):
        if isinstance(value, str):
            if value not in self.municipality_options:
                raise ValueError('Valor inválido para município')
            self.__municipality__ = value
        elif isinstance(value, Iter):
            if all(map(lambda v: type(v) == int, value)):
                try:
                    self.__municipality__ = tuple([k for i, k in enumerate(
                        self.municipality_options.keys()) if i in value])  # type: ignore
                except IndexError:
                    raise IndexError('Indíce inválido para município')
            else:
                if any(map(lambda o: o not in self.municipality_options, value)):
                    raise ValueError('Valor inválido para município')
                self.__municipality__ = tuple(value)  # type: ignore
        else:
            raise TypeError('Tipo inválido para município')

    @period.setter
    def period(self, value: Union[str, int]):
        if isinstance(value, str):
            if value not in self.period_options:
                raise ValueError('Valor inválido para período')
            self.__period__ = value
        elif isinstance(value, int):
            try:
                self.__period__ = list(self.period_options.keys())[value]
            except IndexError:
                raise IndexError(
                    'Opção de índice {} não existe para período'.format(value))
        else:
            raise TypeError('Tipo não suportado para configurar período')

    @index.setter
    def index(self, value: Union[str, int]):
        if isinstance(value, str):
            if value not in self.index_options:
                raise ValueError('Valor inválido para índice')
            self.__index__ = value
        elif isinstance(value, int):
            try:
                self.__index__ = list(self.index_options.keys())[value]
            except IndexError:
                raise IndexError(
                    'Opção de índice {} não existe para índice'.format(value))
        else:
            raise TypeError('Tipo não suportado para configurar índice')

    @view.setter
    def view(self, value: Union[str, int]):
        if isinstance(value, str):
            if value not in self.view_options:
                raise ValueError('Valor inválido para visão de equipe')
            self.__view__ = value
        elif isinstance(value, int):
            try:
                self.__view__ = list(self.view_options.keys())[value]
            except IndexError:
                raise IndexError(
                    'Opção de índice {} não existe para visão de equipe'.format(value))
        else:
            raise TypeError('Tipo não suportado para configurar índice')

    # }}}

    def post(  # {{{
        self,
        params: dict = dict(),
        output: Union[str, TextIO] = None,
        strip: bool = False
    ) -> None:
        """Faz uma requisição POST ao Sisab como pelo navegador. {{{

            @param params
                    Os pares de chave-valor passados na URL da requisição
                    São mesclados com parâmetros padrão (e podem substituí-los)
            @param output
                    O nome do arquivo para salvar a resposta da requisição
                    Quando não é passado, a resposta não é salva
                    }}} """

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "sisab.saude.gov.br",
            "User-Agent":
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0)" +
                " Gecko/20100101 Firefox/91.0",
            "Accept":
                "text/html,application/xhtml+xml,application/xml;" +
                "q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,en-US;q=0.8,en;q=0.5,pt;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://sisab.saude.gov.br",
            "Connection": "keep-alive",
            "Referer":
                "https://sisab.saude.gov.br/paginas/acessoRestrito/" +
                "relatorio/federal/indicadores/indicadorPainel.xhtml",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Cookie": ';'.join(self.__cookies__),
        }

        default = {
            "j_idt50": "j_idt50",
            "javax.faces.ViewState": self.__view_state__,
            "coIndicador": self.index,
            "quadrimestre": self.period,
            "visaoEquipe": self.view
        }
        default.update(params)

        res = req.post(Sisab.URL, headers=headers, params=default)
        content_type, _ = res.headers['Content-Type'].split(';')

        # Somente faz o parse do HTML se a resposta for xml
        text = res.text
        if content_type == 'text/xml':
            # FIXME: A resposta vem no encoding ISO-8859-1, não UTF-8
            # self.__last_request__ = bytes(res.text, encoding=encoding.split('=')[1]).decode('utf-8')
            self.__last_request__ = text
            self.__update_view_state__(text)
        elif content_type == 'text/csv':
            if isinstance(strip, bool):
                _, text, _ = text.split('\n\n\n')
                _, text = text.split('\n', maxsplit=1)
            else:
                text = text.split('\n\n\n')
                strip = [i for i, s in enumerate(strip) if s]
                text = '\n'.join([t for i, t in enumerate(text) if i in strip])

        if output is not None:
            if isinstance(output, str):
                with open(output, 'w') as f:
                    f.write(text + '\n')
            else:
                output.write(text + '\n')
        # }}}

    def __update_view_state__(self, data):  # {{{
        soup = BeautifulSoup(data, 'html.parser')
        el = soup.find('input', id='javax.faces.ViewState')
        if isinstance(el, Tag):
            self.__view_state__ = el.attrs.get('value', '')
        else:
            el = soup.find('update', id='javax.faces.ViewState')
            if isinstance(el, Tag):
                self.__view_state__ = el.text
            else:
                raise ValueError('Não foi possível encontrar o ViewState')
        # }}}

    def __get_cookies__(self):  # {{{
        res = req.get(Sisab.URL)
        self.__cookies__ = list(map(
            lambda c: c.split(';')[0],
            res.headers['Set-Cookie'].split(', ')
        ))
        self.__last_request__ = res.text
        self.__update_view_state__(res.text)
        soup = BeautifulSoup(res.text, 'html.parser')

        el = soup.find('select', id='quadrimestre')
        if isinstance(el, Tag):
            el = el.findAll('option')
            self.__period_options__ = {
                o.get('value'): o.text
                for o in el
                if isinstance(o, Tag) and o.get('value') != ''
            }  # type: ignore

        el = soup.find('select', id='coIndicador')
        if isinstance(el, Tag):
            el = el.findAll('option')
            self.__index_options__ = {
                o.get('value'): o.text
                for o in el
                if isinstance(o, Tag) and o.get('value') != ''
            }  # type: ignore

        el = soup.find('select', id='visaoEquipe')
        if isinstance(el, Tag):
            el = el.findAll('option')
            self.__view_options__ = {
                o.get('value'): o.text
                for o in el
                if isinstance(o, Tag) and o.get('value') != ''
            }  # type: ignore
        # }}}

    @must_set('area')
    def update_area(self):  # {{{
        self.post({
            'selectLinha': self.area,
            'javax.faces.source': 'selectLinha',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute': 'selectLinha selectLinha',
            'javax.faces.partial.render': 'regioes script',
            'javax.faces.behavior.event': 'valueChange',
            'javax.faces.partial.ajax': 'true'
        })
        # }}}

    @must_set('area')
    def get_area(self, file: str, strip: bool = False):  # {{{
        s.post({
            'selectLinha': self.area,
            'j_idt84': 'j_idt84'
        }, file, strip)
        # }}}

    @must_set('area')
    def update_region(self):  # {{{
        self.post({
            'selectLinha': self.area,
            'javax.faces.source': 'selectLinha',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute': 'selectLinha selectLinha',
            'javax.faces.partial.render': 'regioes script',
            'javax.faces.behavior.event': 'valueChange',
            'javax.faces.partial.ajax': 'true'
        })
        soup = BeautifulSoup(self.__last_request__, 'html.parser')
        el = soup.find('update', id='regioes')
        if isinstance(el, Tag):
            soup = BeautifulSoup(el.text, 'html.parser').findAll('option')
            self.__region_options__ = {o.get('value'): o.text for o in soup if isinstance(
                o, Tag) and o.get('value') != ''}  # type: ignore
        else:
            raise TypeError('Não foi possível encontrar a Tag de id "regioes"')
        # }}}

    @must_set('area', 'region')
    def get_region(self, file: str, strip: bool = False):  # {{{
        s.post({
            'selectLinha': self.area,
            'regiao': self.region,
            'j_idt84': 'j_idt84'
        }, file, strip)
        # }}}

    @must_set('area')
    def update_state(self, look_into='estados'):  # {{{
        self.post({
            'selectLinha': self.area,
            'javax.faces.source': 'selectLinha',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute': 'selectLinha selectLinha',
            'javax.faces.partial.render': 'regioes script',
            'javax.faces.behavior.event': 'valueChange',
            'javax.faces.partial.ajax': 'true'
        })
        soup = BeautifulSoup(self.__last_request__, 'html.parser')
        el = soup.find('update', id='regioes')
        if isinstance(el, Tag):
            soup = BeautifulSoup(el.text, 'html.parser').find(
                'select', id=look_into)
            if isinstance(soup, Tag):
                soup = soup.findAll('option')
                self.__state_options__ = {o.get('value'): o.text for o in soup if isinstance(
                    o, Tag) and o.get('value') != ''}  # type: ignore
            else:
                raise TypeError(
                    'Não foi possível encontrar a Tag de id', look_into)
        else:
            raise TypeError('Não foi possível encontrar a Tag de id "regioes"')
        # }}}

    @must_set('area')
    def get_state(self, file: str, strip: bool = False):  # {{{
        params = {
            'selectLinha': self.area,
            'j_idt84': 'j_idt84'
        }
        if len(self.state) > 0:
            params['estados'] = self.state  # type: ignore

        s.post(params, file, strip)
        # }}}

    @must_set('area', 'state')
    def update_municipality(self):  # {{{
        self.post({
            'selectLinha': self.area,
            'estadoMunicipio': self.state,
            'javax.faces.source': 'estadoMunicipio',
            'javax.faces.partial.event': 'change',
            'javax.faces.partial.execute': 'estadoMunicipio estadoMunicipio',
            'javax.faces.partial.render': 'regioes script',
            'javax.faces.behavior.event': 'valueChange',
            'javax.faces.partial.ajax': 'true'
        })
        soup = BeautifulSoup(self.__last_request__, 'html.parser')
        el = soup.find('update', id='regioes')
        if isinstance(el, Tag):
            soup = BeautifulSoup(el.text, 'html.parser').find(
                'select', id='municipios')
            if isinstance(soup, Tag):
                soup = soup.findAll('option')
                self.__municipality_options__ = {o.get('value'): o.text for o in soup if isinstance(
                    o, Tag) and o.get('value') != ''}  # type: ignore
            else:
                raise TypeError(
                    'Não foi possível encontrar a Tag de id "municipios"')
        else:
            raise TypeError('Não foi possível encontrar a Tag de id "regioes"')
        # }}}

    @must_set('area', 'state')
    def get_municipality(self, file: str, strip: bool = False):  # {{{
        params = {
            'selectLinha': self.area,
            'estadoMunicipio': self.state,
            'j_idt84': 'j_idt84'
        }
        if len(self.municipality) > 0:
            params['municipios'] = self.municipality

        s.post(params, file, strip=strip)
        # }}}
    # }}}

    def get_data(self, area, file, strip=True, **options):
        # Faz as requisições desde o começo até o fim
        self.area = area
        if 'period' in options:
            self.period = options['period']
        if 'index' in options:
            self.index = options['index']
        if 'view' in options:
            self.view = options['view']
        if self.area == 'nacional':
            self.get_area(file, strip=strip)
        elif self.area == 'regiao':
            self.update_region()
            self.region = options['region']
            self.get_region(file, strip=strip)
        elif self.area == 'uf':
            self.update_state()
            if 'state' in options:
                self.state = options['state']
            self.get_state(file, strip=strip)
        elif self.area == 'ibge':
            self.update_state(look_into='estadoMunicipio')
            self.state = options['state']
            self.update_municipality()
            if 'municipality' in options:
                self.municipality = options['municipality']
            self.get_municipality(file, strip=strip)


if __name__ == '__main__':
    import shutil
    # view_options = Visao, period_options = Quadrimestres, state_options = Estados, area_options = Nivel de Visualizacao, Indicador
    s = Sisab()
    s.area = 'ibge'
    s.view = 0
    s.update_state(look_into='estadoMunicipio')
    print('1) ARQUIVO GLOBAL CSV', '2) PEQUENOS ARQUIVOS', sep='\n')
    resposta = int(input())
    print('\033[2J')

    tc, tl = shutil.get_terminal_size()
    if resposta == 1:
        max_bar = tc - 9
        with open('out.csv', 'w') as file:
            # for p, i, view in [(p, i, view) for p in s.period_options for i in s.index_options for view in s.view_options]:
            for p, i in [(p, i) for p in s.period_options for i in s.index_options]:
                strip = [True, True, False]
                file.write('\n')
                print()  # Texto "Baixando ..."
                print('Período:'.ljust(15), s.period_options[p][:tc - 16])
                print('Indicador:'.ljust(15), s.index_options[i][:tc - 16])
                print('Visualização:'.ljust(15),
                      s.view_options[s.view][:tc - 16])
                print()  # Barra de progresso
                print('\033[5A', end='')
                for idx, uf in enumerate(s.state_options):
                    s.state = uf
                    s.update_municipality()
                    s.get_data(s.area, file, state=uf,
                               period=p, index=i, view=s.view, strip=strip)
                    strip = True
                    print('\033[2K\r\033[1mBAIXANDO\033[31m',
                          s.state_options[uf], '\033[0m\033[4B', end='')
                    pct = (idx * max_bar) / len(s.state_options)
                    pct_str = '{:3.2f}%'.format(pct)
                    pct_str = pct_str.rjust(7)
                    decimal = pct - int(pct)
                    pct_half = '▌' if decimal > 0.5 else ''
                    print(
                        # Limpa a linha e imprime a porcentagem
                        '\033[2K\r{}'.format(pct_str),
                        # Imprime a barra de progresso
                        '█' * int(pct) + pct_half + '_' * \
                        (max_bar - int(pct) - len(pct_half)),
                        '\033[4A', end='')  # Volta para a linha "BAIXANDO ..."
                print('\033[2K\r\033[1mFINALIZADO!!\033[0m\033[4B', end='')
                print('\033[2K\r100.00% ' + '█' * max_bar)
                print()
    elif resposta == 2:
        for uf, p, i, view in [(uf, p, i, view) for uf in s.state_options for p in s.period_options for i in s.index_options for view in s.view_options]:
            s.state = uf
            s.update_municipality()
            s.get_data(s.area, '{}{}{}{}.csv'.format(
                s.state_options[uf],
                s.period_options[p],
                s.index_options[i],
                s.view_options[view]),
                state=uf,
                period=p, index=i, view=view)
            print("\033[2K\r BAIXANDO",
                  s.state_options[uf],
                  s.period_options[p],
                  s.index_options[i],
                  s.view_options[view],
                  end='')
