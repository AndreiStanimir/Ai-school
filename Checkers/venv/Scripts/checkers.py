from logging import setLogRecordFactory
import time
import random
from copy import copy
from copy import deepcopy

"""
jucatorul primeste o lista cu piesele pe care le poate muta si unde le poate muta

reguli neimplementate:
    - verificare remiza
"""


class Stare:
    pass


class Joc:
    NR_COLOANE = 8
    NR_LINII = 8

    SIMBOLURI_JUC = ['n', 'a']
    JMIN = 'a'
    JMAX = 'n'
    GOL = '·'

    OPPONENT_MULTIPLIER=1
    get_opponent = {'A': ['n', 'N'],
                    'a': ['n', 'N'],
                    'N': ['a', 'A'],
                    'n': ['a', 'A']}

    def __init__(self, tabla=None):
        self.matr = tabla or [['·', 'a', '·', 'a', '·', 'a', '·', 'a'],
                              ['a', '·', 'a', '·', 'a', '·', 'a', '·'],
                              ['·', 'a', '·', 'a', '·', 'a', '·', 'a'],
                              ['·', '·', '·', '·', '·', '·', '·', '·'],
                              ['·', '·', '·', '·', '·', '·', '·', '·'],
                              ['n', '·', 'n', '·', 'n', '·', 'n', '·'],
                              ['·', 'n', '·', 'n', '·', 'n', '·', 'n'],
                              ['n', '·', 'n', '·', 'n', '·', 'n', '·']]
        # self.matr = tabla or [['·', 'a', '·', 'a', '·', 'a', '·', 'a'],
        #                       ['a', '·', 'a', '·', '·', '·', 'a', '·'],
        #                       ['·', '·', '·', 'a', '·', 'a', '·', 'a'],
        #                       ['·', '·', '·', '·', '·', '·', '·', '·'],
        #                       ['·', 'a', '·', '·', '·', '·', '·', '·'],
        #                       ['n', '·', 'n', '·', 'n', '·', 'n', '·'],
        #                       ['·', 'n', '·', 'n', '·', 'n', '·', 'n'],
        #                       ['n', '·', 'n', '·', 'n', '·', 'n', '·']]

    def final(self, jucator):
        # verifica daca 'jucator' mai are mutari
        # returneaza 'False' daca nu s-a terminat jocul

        for i in range(Joc.NR_COLOANE):
            for j in range(Joc.NR_COLOANE):
                # if self.matr[i][j].isalpha():
                if self.matr[i][j].lower() == jucator:
                    lista_mutari = self.mutari_piesa(i, j)
                    if len(lista_mutari) > 0:
                        return False
        return jucator

    def mutari_piesa(self, l, c, must_move=False):
        # returneaza o lista de coordonate unde poate fi mutata piesa de pe l,c
        lista_mutari = []
        if self.matr[l][c].isupper():
            attack = self.white_check_capture(l, c, must_move, lista_mutari)
            attack = self.black_check_capture(l, c, must_move, lista_mutari)
            if must_move:
                return attack, lista_mutari
            indicies = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for x, y in indicies:
                if 0 <= l + x < Joc.NR_LINII and 0 <= c + y < Joc.NR_COLOANE:
                    if self.matr[l + x][c + y] == '·':
                        lista_mutari.append((l + x, c + y))

        if self.matr[l][c] == 'a':
            attack = self.white_check_capture(l, c, must_move, lista_mutari)
            if must_move:
                return attack, lista_mutari
            indicies = [(1, 1), (1, -1)]
            for x, y in indicies:
                if 0 <= l + x < Joc.NR_LINII and 0 <= c + y < Joc.NR_COLOANE:
                    if self.matr[l + x][c + y] == '·':
                        lista_mutari.append((l + x, c + y))
        elif self.matr[l][c] == 'n':
            attack = self.black_check_capture(l, c, must_move, lista_mutari)
            if must_move:
                return attack, lista_mutari
            indicies = [(-1, 1), (-1, -1)]
            for x, y in indicies:
                if 0 <= l + x < Joc.NR_LINII and 0 <= c + y < Joc.NR_COLOANE:
                    if self.matr[l + x][c + y] == '·':
                        lista_mutari.append((l + x, c + y))
        return must_move, lista_mutari

    def black_check_capture(self, l, c, must_move, lista_mutari):
        indicies = [(-2, 2), (-2, -2)]
        for x, y in indicies:
            if 0 <= l + x < Joc.NR_LINII and 0 <= c + y < Joc.NR_COLOANE:
                if self.matr[l + x][c + y] == '·' and self.matr[l + x // 2][c + y // 2] in self.get_opponent[
                    self.matr[l][c]]:
                    must_move = True
                    lista_mutari.append((l + x, c + y))
        if len(lista_mutari)==0:
            return False
        return must_move

    def white_check_capture(self, l, c, must_move, lista_mutari):
        indicies = [(2, 2), (2, -2)]
        for x, y in indicies:
            if 0 <= l + x < Joc.NR_LINII and 0 <= c + y < Joc.NR_COLOANE:
                if self.matr[l + x][c + y] == '·' and self.matr[l + x // 2][c + y // 2] in self.get_opponent[
                    self.matr[l][c]]:
                    must_move = True
                    lista_mutari.append((l + x, c + y))
        if len(lista_mutari)==0:
            return False
        return must_move
    def mutari(self, stare: Stare):
        jucator = stare.j_curent
        if stare.must_move_piece is not None:
            l, c = stare.must_move_piece
            must_move, mutari_gasite = self.mutari_piesa(l, c)
            if len(mutari_gasite)==0:
                stare.must_move_piece=None
                return [(l,c,[])]
            return [(l, c, mutari_gasite)]
        l_mutari = []
        player_must_capture = False

        for l in range(Joc.NR_COLOANE):
            for c in range(Joc.NR_COLOANE):
                if self.matr[l][c].lower() == jucator:
                    must_move, mutari_gasite = self.mutari_piesa(l, c)
                    if len(mutari_gasite)==0:
                        continue
                    if must_move and not player_must_capture:
                        l_mutari.clear()  # daca jucatorul poate captura, sterg mutarile gasite inainte, care nu erau modalitati de a captura
                        player_must_capture = True
                    if len(mutari_gasite) > 0 and (must_move == player_must_capture):
                        l_mutari.append((l, c, mutari_gasite))
        return l_mutari

    def fct_euristica(self):
        # idee de euristica luata de pe www.cs.columbia.edu/~devans/TIC/AB.html
        # daca schimbam jucatorii intre ei, schimbam semnul la valori
        valori_piese = {'a': -3 *Joc.OPPONENT_MULTIPLIER,
                        'A': -5 *Joc.OPPONENT_MULTIPLIER,
                        'n': 3 *Joc.OPPONENT_MULTIPLIER,
                        'N': 5 *Joc.OPPONENT_MULTIPLIER,
                        '·': 0
                        }

        diferenta_piese = 0
        for i in range(Joc.NR_LINII):
            for p in self.matr[i]:
                diferenta_piese += valori_piese[p]
        return diferenta_piese

    def fct_euristica2(self, piesa=5, rege=7.75, back_row=4, mid_box=2.5):
        valori_piese = {'a': -piesa *Joc.OPPONENT_MULTIPLIER,
                        'A': -rege *Joc.OPPONENT_MULTIPLIER,
                        'n': piesa *Joc.OPPONENT_MULTIPLIER,
                        'N': rege *Joc.OPPONENT_MULTIPLIER,
                        '·': 0
                        }
        rege*=Joc.OPPONENT_MULTIPLIER
        back_row*=Joc.OPPONENT_MULTIPLIER
        mid_box*=Joc.OPPONENT_MULTIPLIER
        diferenta_piese = 0
        for i in range(Joc.NR_LINII):
            for p in self.matr[i]:
                diferenta_piese += valori_piese[p]

        # evaluate backrows
        for i in range(0, self.NR_COLOANE):
            if self.matr[0][i] in ('a', 'A'):
                diferenta_piese -= mid_box
            if self.matr[self.NR_LINII - 1][i] in ('n', 'N'):
                diferenta_piese += mid_box

        # evaluate center of the board
        for l in range(3, 5):
            for c in range(2, 7):
                p = self.matr[l][c]
                if p in ('a', 'A'):
                    diferenta_piese -= mid_box
                elif p in ('n', 'N'):
                    diferenta_piese += mid_box
        return diferenta_piese

    def estimeaza_scor(self, adancime, jucator_curent):
        t_final = self.final(jucator_curent)
        if t_final == Joc.JMAX:
            return (9999 + adancime)*-Joc.OPPONENT_MULTIPLIER
        elif t_final == Joc.JMIN:
            return (-9999 - adancime)*-Joc.OPPONENT_MULTIPLIER
        elif t_final == 'remiza':
            return 0
        else:
            return self.fct_euristica2()

    def promoveaza(self, l, c):
        # daca piesa se afla pe ultimul rank, devine rege
        if self.matr[l][c] == 'a' and l == self.NR_LINII - 1:
            self.matr[l][c] = 'A'
        elif self.matr[l][c] == 'n' and l == 0:
            self.matr[l][c] = 'N'

    def __str__(self):
        sir = '  '

        #for nr_col in range(ord('a'), ord('h') + 1):
        for nr_col in range(self.NR_LINII):
            sir += str(nr_col) + ' '
        sir += '\n'

        for i in range(self.NR_COLOANE):
            sir += str(i) + '|'
            sir = sir + ''.join(" ".join(self.matr[i])) + '\n'
        return sir


class Stare:
    ADANCIME_MAX = None

    def __init__(self, tabla_joc: Joc, j_curent, adancime, draw_counter=0, must_move_piece=None, parinte=None,
                 scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # daca face o captura, jucatorul trebuie sa captureze din nou cu aceeasi pieasa (daca este posibil)
        self.must_move_piece = must_move_piece

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

        self.draw_counter = draw_counter

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def get_starile_urmatoare(self):
        # returneaza toate starile posibile
        l_stari_mutari = []
        l_mutari = self.tabla_joc.mutari(self)
        juc_opus = self.j_curent
        if self.must_move_piece is not None:
            #print(l_mutari)
            if len(l_mutari[0][2]) == 0:
                juc_opus = self.jucator_opus()
                return [Stare(self.tabla_joc, juc_opus, self.adancime - 1, draw_counter= self.draw_counter + 1, parinte=self)]

        else:
            juc_opus = self.jucator_opus()

        tabla_noua = None
        for l, c, mutari in l_mutari:
            for m in mutari:
                tabla_noua = deepcopy(self.tabla_joc)
                l_stari_mutari.append(
                    Stare(tabla_noua, juc_opus, self.adancime - 1, draw_counter= self.draw_counter + 1, parinte=self, ))
                l_stari_mutari[-1].muta(l, c, m)

        return l_stari_mutari

    def muta(self, l, c, dest):
        # muta piesa de pe l,c la destinatie
        l_dest, c_dest = dest
        self.tabla_joc.matr[l_dest][c_dest] = self.tabla_joc.matr[l][c]
        self.promoveaza(l_dest, c_dest)
        self.tabla_joc.matr[l][c] = '·'
        if abs(l_dest - l) == 2:  # captura
            self.draw_counter=0
            self.tabla_joc.matr[l + (l_dest - l) // 2][c + (c_dest - c) // 2] = '·'
            if len(self.tabla_joc.mutari_piesa(l_dest, c_dest, True)) > 0:
                self.must_move_piece = (l_dest, c_dest)
                return True
            else:
                self.must_move_piece = None
        else:
            self.draw_counter+=1
            self.must_move_piece = None
        return False

            # self.muta(l_dest, c_dest, dest[1:])

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent: " + self.j_curent + ")\n"
        return sir

    def promoveaza(self, l, c):
        if self.tabla_joc.matr[l][c] == 'a' and l == self.tabla_joc.NR_LINII - 1:
            self.tabla_joc.matr[l][c] = 'A'
        elif self.tabla_joc.matr[l][c] == 'n' and l == 0:
            self.tabla_joc.matr[l][c] = 'N'


""" Algoritmul MinMax """


def min_max(stare):
    if stare.draw_counter==50:
        stare.scor=0
        return stare
    if stare.adancime == 0 or stare.tabla_joc.final(stare.j_curent):
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime,stare.j_curent)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.get_starile_urmatoare()

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        # daca jucatorul e JMAX aleg starea-fiica cu scorul maxim
        if len(mutari_scor) == 0:
            stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime, stare.j_curent)
            return stare
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # daca jucatorul e JMIN aleg starea-fiica cu scorul minim
        if len(mutari_scor) == 0:
            stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime, stare.j_curent)
            return stare
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)

    stare.scor = stare.stare_aleasa.scor
    return stare


def alpha_beta(alpha, beta, stare):
    if stare.draw_counter >= 50:
        stare.scor = 0
        return stare
    if stare.adancime == 0 or stare.tabla_joc.final(stare.j_curent):
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime, stare.j_curent)
        return stare

    if alpha >= beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.get_starile_urmatoare()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza scorul
            stare_noua = alpha_beta(alpha, beta, mutare)

            if  scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if alpha < stare_noua.scor and stare_noua.scor<=0:
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')

        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor and stare_noua.scor>=0:
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    if stare.stare_aleasa is None:
        stare.scor = 0
        return stare
    stare.scor = stare.stare_aleasa.scor

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final(stare_curenta.j_curent)
    if (final):
        if (final == "remiza"):
            print("Remiza!")
        else:
            print("A castigat " + stare_curenta.jucator_opus())

        return True

    return False


def main():
    joc_automat = True
    raspuns_valid = False

    algoritm=None;
    while algoritm is None:
        raspuns=input("1 pentru min_max\n2 pentru alpha_beta ")
        if raspuns=='1':
            algoritm=min_max
        elif raspuns=='2':
            algoritm=alpha_beta
    adancimi = [2, 5, 8]
    nivel = input_dificultate()
    Stare.ADANCIME_MAX = adancimi[nivel - 1]

    #joc_automat = input_joc_automat()

    culoare_piese=None
    while culoare_piese is None:
        raspuns = input("n pentru negre\na pentru albe ")
        if raspuns == 'n':
            culoare_piese='n'
        elif raspuns == 'a':
            culoare_piese = 'a'


    tabla_curenta = Joc()
    print("Tabla initiala")
    print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, 'n', Stare.ADANCIME_MAX)

    linie = -1
    coloana = -1
    if culoare_piese == 'n':
        Joc.JMIN,Joc.JMAX=Joc.JMAX,Joc.JMIN
        Joc.OPPONENT_MULTIPLIER=-1
    #     stare_curenta.j_curent = Joc.JMIN
    # else:
    #     stare_curenta.j_curent=Joc.JMAX
    timp_inceput_joc = time.time() * 1000
    while True:
        #print(stare_curenta.draw_counter)
        #print(stare_curenta.tabla_joc.estimeaza_scor(0,stare_curenta.j_curent))
        if stare_curenta.draw_counter==50:
            print("remiza")
            return
        if stare_curenta.j_curent == Joc.JMIN:
            # muta jucatorul
            t_inainte = time.time() * 1000
            raspuns_valid = False
            mutari_juc = stare_curenta.tabla_joc.mutari(stare_curenta)
            if len(mutari_juc) == 0 or mutari_juc is None:
                print("A castigat ",Joc.JMAX)
                break
            if joc_automat:
                l, c, dest = random.choice(mutari_juc)
                stare_curenta.muta(l, c, dest[0])
                #time.sleep(1)
                raspuns_valid = True
            print(*mutari_juc, sep='\n')
            repeta=False
            while not raspuns_valid:
                try:
                    coloana, linie = input_mutare(coloana, linie, stare_curenta)
                    #coloana = ord(coloana) - ord('a')

                    linie=int(linie)
                    coloana=int(coloana)
                    # casuta goala de pe acea "coloana"
                    if 0 <= linie < Joc.NR_LINII and (0 <= coloana < Joc.NR_COLOANE):
                        # coloana=ord(coloana)-ord('a')
                        for l, c, mutari_posibile in mutari_juc:
                            if len(mutari_posibile)==0:

                                continue;
                            if l == linie and c == coloana:
                                if len(mutari_posibile) == 1:
                                    repeta = stare_curenta.muta(l, c, mutari_posibile[0])
                                    break
                                print(mutari_posibile)
                                coloana, linie = input_mutare(coloana, linie, stare_curenta)
                                for m in mutari_posibile:
                                    if (linie, coloana) == m:
                                        repeta = stare_curenta.muta(l, c, m)

                        raspuns_valid = True
                    else:
                        print("Coloana invalida (trebuie sa fie un numar intre 0 si {}).".format(Joc.NR_COLOANE - 1))
                    # if ........
                    # ..........

                    # if ......
                    #    print("Toata coloana este ocupata.")

                except ValueError:
                    print("Coloana trebuie sa fie un numar intreg.")

            t_dupa = time.time() * 1000
            t_mutare = round(t_dupa - t_inainte, 2)
            print("Jucatorul a \"gandit\" timp de " + str(t_mutare) + " milisecunde ")
            # afisarea starii jocului in urma mutarii utilizatorului
            print("\nTabla dupa mutarea jucatorului")
            print(str(stare_curenta))

            # testez daca jocul a ajuns intr-o stare finala
            # si afisez un mesaj corespunzator in caz ca da
            if (afis_daca_final(stare_curenta)):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            if not repeta:
                stare_curenta.j_curent = stare_curenta.jucator_opus()

        # --------------------------------
        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator

            # preiau timpul in milisecunde de dinainte de mutare        
            t_inainte = time.time() * 1000
            if algoritm==alpha_beta:
                stare_actualizata = alpha_beta(-5000, 5000, stare_curenta)
            else:
                stare_actualizata=min_max(stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = time.time() * 1000
            print("Calculatorul a \"gandit\" timp de " + str(round(t_dupa - t_inainte, 2)) + " milisecunde.")

            if (afis_daca_final(stare_curenta)):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            if stare_curenta.must_move_piece is None:
                stare_curenta.j_curent = stare_curenta.jucator_opus()

    timp_jucat = round(time.time() * 1000 - timp_inceput_joc, 2)
    print("Jocul a durat " + str(timp_jucat / 1000) + " secunde")


def input_mutare(coloana, linie, stare_curenta):
    linie = input("linie= ")
    if linie == "exit":
        print("Scor calculator: ",
              stare_curenta.tabla_joc.estimeaza_scor(Stare.ADANCIME_MAX, stare_curenta.jucator_opus()))
        exit()
    coloana = input("coloana = ")
    if coloana == "exit":
        print("Scor calculator: ",
              stare_curenta.tabla_joc.estimeaza_scor(Stare.ADANCIME_MAX, stare_curenta.jucator_opus()))
        exit()
    return coloana, linie


def input_joc_automat():
    # jucatorul alege o mutare random de fiecare data
    # joc_automat = input("Jucatorul joaca automat?(y/n)")
    joc_automat = 'y'
    if joc_automat == 'y':
        joc_automat = True
    else:
        joc_automat = False
    return joc_automat


def input_dificultate():
    # joc_automat = input()
    while True:
        raspuns = input("Dificultate?\n1 pentru incepator\n2 pentru mediu\n3 pentru avansat\n")
        if int(raspuns) in [1, 2, 3]:
            return raspuns


if __name__ == "__main__":
    main()
