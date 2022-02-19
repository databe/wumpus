import traceback
import numpy as np
import random
import logging, datetime

class Partida:

    def __init__(self):

        self.tablero = None
        self.tablero_sorteo = None

        self.casilla_salida = None
        self.casilla_actual = None

        #ids para identificar a los protagonistas de la partida
        self.id_jugador = 1
        self.id_wumpus = 2
        self.id_oro = 3
        self.id_pozo = 4

        #cantidad de elementos fijos de la partida
        self.jugador = 1
        self.wumpus = 1
        self.oro = 1
        self.pozos = None
        self.flechas = 0
        self.direccion = 'N' # N, S, E, O
        
        self.movimiento = False
        self.hay_partida = False

        self.num_celdas = self.crear_partida() # importante que esté al final

    def crear_partida(self):
        try:
            self.num_celdas = int(input('\n-------- H U N T  T H E  W U M P U S --------\nBienvenido al juego de WUMPUS.\nIntroduce un número entero igual o mayor que 3 para determinar el tamaño del tablero (3x3, 4x4...) y pula ENTER:\n'))
            if self.num_celdas > 2:
                self.pozos = self.num_celdas - 1 # decido que en la partida hay N-1 pozos
                self.flechas = int(self.num_celdas / 2) # decido que las flechas son N/2
                logging.basicConfig(filename='LOG_WUMPUS.log',format='%(asctime)s |--> %(levelname)s: %(message)s', level=logging.INFO)
                logging.info('\n\n---------------------------------------- NUEVA PARTIDA CREADA @ ' + str(datetime.datetime.now()) + ' ----------------------------------------')
                   
            else:
                return
        except ValueError:
            self.crear_partida()
        
        # creo lista con todos los valores de las celdas
        total_celdas = self.num_celdas ** 2
        celdas_vacias = total_celdas - self.jugador - self.oro - self.wumpus - self.pozos
  
        # creo el tablero NxN para la partida y otro para sortear las celdas
        self.tablero = np.full((self.num_celdas, self.num_celdas), None)

        orden_del_tablero = [0] * celdas_vacias #array de las ids
 
        self.tablero = np.full((self.num_celdas, self.num_celdas), None)
        
        # añado las ids de los personajes, oro y pozos
        orden_del_tablero.extend([self.id_jugador, self.id_wumpus, self.id_oro]) 
        orden_del_tablero.extend([self.id_pozo for i in range(self.pozos)])
        # reordeno aleatoriamente todos los valores del array

        random.shuffle(orden_del_tablero)

        self.tablero_sorteo = np.full((self.num_celdas, self.num_celdas), 0)
        for i in range(len(self.tablero_sorteo)):
            for j in range(len(self.tablero_sorteo)):
                self.tablero_sorteo[i][j] = orden_del_tablero.pop(0)

        self.tablero = self.llenar_tablero(self.tablero, self.tablero_sorteo)
        
        self.casilla_salida = self.get_casilla(self.tablero)
        print(f'casilla_salida: {self.casilla_salida}')
        
        print('\nSE HA CREADO LA PARTIDA!')
        print(f'\nTamaño del tablero: {self.num_celdas}x{self.num_celdas}.\nPozos: {self.pozos}.\nFlechas {self.flechas}.')
        print('\nEl jugador empieza en dirección Norte (N).\nPuede avanzar 1 casilla en cada jugada.\nPuede girar 90º en las 4 puntos cardinales: N-S-E-O.\nPuede lanzar flechas para intentar matar al Wumpus.')
        print('\nCOMANDOS:\n [W + ENTER]: Avanzar 1 casilla.\n [D + ENTER]: Girar 90º Derecha.\n [A + ENTER]: Girar 90º Izquierda.\n [S + ENTER]: Lanzar flechas.\n [Q + ENTER]: Salir (sólo desde la casilla de salida).\n\nSUERTE!')
        
        logging.info(f'\nTamaño del tablero: {self.num_celdas}x{self.num_celdas}.\nPozos: {self.pozos}.\nFlechas {self.flechas}.')  
        logging.info(f'\nid_jugador = 1, id_wumpus = 2, id_oro = 3, id_pozos = 4.\nPosiciones iniciales:\n {self.tablero_sorteo}.')
        logging.info(f'Tablero de la partida:\n {self.tablero}.')

        self.hay_partida = True

        while self.hay_partida:
            
            self.movimiento = True
            self.mover_jugador(self.tablero, self.tablero_sorteo, self.direccion) # empezamos siempre en direccion N
    

    # Comprobar si la celda tiene pistas
    def llenar_tablero(self, partida, sorteo):

        for (x, y), item in np.ndenumerate(sorteo):
            for (i, j), arr in np.ndenumerate(partida):

                celda = {
                    'jugador': False,
                    'flechas': None,
                    'tiene_el_oro': False,
                    'wumpus': False,
                    'oro': False,
                    'pozo': False,
                    'olor': False,
                    'brillo': False,
                    'brisa': False
                }

                partida[x][y] = celda
                
                if item == 1:
                    partida[x][y]['jugador'] = True
                    partida[x][y]['flechas'] = self.flechas
                elif item == 2:
                    partida[x][y]['wumpus'] = True
                elif item == 3:
                    partida[x][y]['oro'] = True
                elif item == 4:
                    partida[x][y]['pozo'] = True
        
        # actualizo celdas de olor, brillo, brisa
        for (x, y), item in np.ndenumerate(sorteo):
            for (i, j), arr in np.ndenumerate(partida):
                if partida[x][y]['wumpus'] == True:
                    if x + 1 < self.num_celdas:
                        partida[x + 1][y]['olor'] = True
                    if x - 1 >= 0:
                        partida[x - 1][y]['olor'] = True
                    if y + 1 < self.num_celdas:
                        partida[x][y + 1]['olor'] = True
                    if y - 1 >= 0:
                        partida[x][y - 1]['olor'] = True
                
                if partida[x][y]['oro'] == True:
                    if x + 1 < self.num_celdas:
                        partida[x + 1][y]['brillo'] = True
                    if x - 1 >= 0:
                        partida[x - 1][y]['brillo'] = True
                    if y + 1 < self.num_celdas:
                        partida[x][y + 1]['brillo'] = True
                    if y - 1 >= 0:
                        partida[x][y - 1]['brillo'] = True
                
                if partida[x][y]['pozo'] == True:
                    if x + 1 < self.num_celdas:
                        partida[x + 1][y]['brisa'] = True
                    if x - 1 >= 0:
                        partida[x - 1][y]['brisa'] = True
                    if y + 1 < self.num_celdas:
                        partida[x][y + 1]['brisa'] = True
                    if y - 1 >= 0:
                        partida[x][y - 1]['brisa'] = True

        return partida


    def check_accion(self):
        botones = ['W', 'S', 'D', 'A', 'Q']
        botones_giro = ['A', 'D']
        try:
            accion = str(input('Avanza [ W ], Gira [ A ]-[ D ], Dispara [ S ] o Sal del juego [ Q ]:\n')).upper()
            
            if accion in botones:
                
                if accion == 'A':
                    if self.direccion == 'N':
                        self.direccion = 'O'
                    elif self.direccion == 'S':
                        self.direccion = 'E'
                    elif self.direccion == 'E':
                        self.direccion = 'N'
                    elif self.direccion == 'O':
                        self.direccion = 'S'
                    
                    logging.info(f'El jugador ha girado a la izquierda y ahora va en direccion {self.direccion}')
                    return accion, self.direccion

                elif accion == 'D':
                    if self.direccion == 'N':
                        self.direccion = 'E'
                    elif self.direccion == 'S':
                        self.direccion = 'O'
                    elif self.direccion == 'E':
                        self.direccion = 'S'
                    elif self.direccion == 'O':
                        self.direccion = 'N'
                    
                    logging.info(f'El jugador ha girado a la derecha y ahora va en direccion {self.direccion}')
                    return accion, self.direccion
                else:
                    
                    return accion, self.direccion

            else:
                logging.info(f'El jugador ha introducido un comando no permitido:\n {accion}.')
                print('\nHA INTRODUCIDO UN COMANDO NO PERMITIDO. INTRODUZCA UNO VÁLIDO.')
                self.check_accion()

        except ValueError:
            print('\nHA INTRODUCIDO UN COMANDO NO PERMITIDO. INTRODUZCA UNO VÁLIDO.')
            logging.info(f'Ha ocurrido algo cuando el jugador ha introducido el comando no permitido:\n {accion}.')
            self.check_accion()
        
        

    def mover_jugador(self, partida, sorteo, direccion):
        
        logging.info(f'El jugador está en direccion {self.direccion}')
        acciones_giro = ['A', 'D']

        if self.es_iterable(partida):
            while self.movimiento:
                for (x, y), arr in np.ndenumerate(partida):

                    if arr['jugador']: # si es la casilla del jugador
                        if arr['olor']:
                            print('\nCUIDADO!! HUELE A WUMPUS!! PODRÍA DISPARARLE UNA FLECHA, O MOVERME CON CUIDADO...')
                        if arr['brillo']:
                            print('\n BIEN!! EL ORO ESTÁ CERCA, VEO SU REFLEJO!!')
                        if arr['brisa']:
                            print('\nCUIDADO!! SIENTO LA BRISA DE UN POZO CERCANO...PODRÍA CAERME!!')
                        
                        
                        if self.direccion == 'N':
                            try:
                                print(f'Voy en direccion NORTE')
                                keys = self.check_accion()
                                if keys[0] == 'W':
                               
                                    if (y + 1) >= self.num_celdas:
                                        print('\nBOOM!! CHOCASTE CONTRA UN MURO! PRUEBA EN OTRA DIRECCIÓN.')
                                        break

                                    else:
                                        partida[x][y + 1]['jugador'] = True
                                        partida[x][y + 1]['flechas'] = self.flechas
                                        partida[x][y]['jugador'] = False
                                        partida[x][y]['flechas'] = 0

                                        sorteo[x][y + 1] = 1
                                        sorteo[x][y] = 0

                                        self.tablero = partida
                                        self.tablero_sorteo = sorteo

                                        if partida[x][y + 1]['wumpus']:
                                            print('\nHAS SIDO ELIMINADO POR EL WUMPUS.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador fue eliminado por el Wumpus:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break

                                        elif partida[x][y + 1]['pozo']:
                                            print('\nHAS CAIDO EN UN POZO Y HAS SIDO ELIMINADO.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador calló en un pozo y quedó eliminado:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break

                                        elif partida[x][y + 1]['oro']:
                                            partida[x][y + 1]['oro'] = False
                                            partida[x][y + 1]['tiene_el_oro'] = True
                                            # actualizo las celdas del brillo
                                            if x + 1 < self.num_celdas:
                                                partida[x + 1][y + 1]['brillo'] = False
                                            if x - 1 >= 0:
                                                partida[x - 1][y + 1]['brillo'] = False
                                            if y + 2 < self.num_celdas:
                                                partida[x][y + 2]['brillo'] = False
                                            if y >= 0:
                                                partida[x][y]['brillo'] = False
                                            self.tablero = partida
                                            logging.info(f'El jugador encontró el oro. El tablero queda así:\n{self.tablero_sorteo}')
                                            print('\nTENGO EL ORO!! HE DE VOLVER VIVO A LA CASILLA DE SALIDA!!!!.\n')
        

                                        else:
                                            logging.info(f'El jugador avanza una casilla. El tablero queda así:\n{self.tablero_sorteo}')
                                            print("avanzo una casilla...")
                                            break
                                        
                                
                                elif keys[0] == 'S':
                                    self.lanzar_flecha(self.tablero, self.tablero_sorteo, x, y)
                                
                                elif keys[0] == 'A': # izquierda A
                                    self.direccion = keys[1]
                                    print('\nHas girado 90º a la izquierda. Vas en dirección OESTE')
                                    break
                                elif keys[0] == 'D': # derecha D
                                    self.direccion = keys[1]
                                    print('\nHas girado 90º a la derecha. Vas en dirección ESTE')
                                    break
                                elif keys[0] == 'Q':
                                    self.casilla_actual = self.get_casilla(self.tablero)
                                    salir = self.salir_partida(self.casilla_salida, self.casilla_actual)
                                    if salir:
                                        print(salir)
                                        self.movimiento = False
                                        self.hay_partida = False
                                        break
                                    else:
                                        break
                            
                            except TypeError:
                                pass
                            except Exception as e:
                                print('\nAlgo ha ocurrido\n')
                                traceback.print_exc()
                                break
                                
                        elif self.direccion == 'S':
                            try:
                                print(f'Voy en direccion SUR')
                                keys = self.check_accion()
                                if keys[0] == 'W':
                                    if (y - 1) < 0:
                                        print('\nBOOM!! CHOCASTE CONTRA UN MURO! PRUEBA EN OTRA DIRECCIÓN.')
                                        break
                                    else:
                                        partida[x][y - 1]['jugador'] = True
                                        partida[x][y - 1]['flechas'] = self.flechas
                                        partida[x][y]['jugador'] = False
                                        partida[x][y]['flechas'] = 0

                                        sorteo[x][y - 1] = 1
                                        sorteo[x][y] = 0

                                        self.tablero = partida
                                        self.tablero_sorteo = sorteo
                                        
                                        if partida[x][y - 1]['wumpus']:
                                            print('\nHAS SIDO ELIMINADO POR EL WUMPUS.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador fue eliminado por el Wumpus:\n{self.tablero_sorteo}')
                                            print(sorteo)
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x][y - 1]['pozo']:
                                            print('\nHAS CAIDO EN UN POZO Y HAS SIDO ELIMINADO.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador calló en un pozo y quedó eliminado:\n{self.tablero_sorteo}')
                                            print(sorteo)
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x][y - 1]['oro']:
                                            partida[x][y - 1]['oro'] = False
                                            partida[x][y - 1]['tiene_el_oro'] = True
                                            # actualizo las celdas del brillo
                                            if x + 1 < self.num_celdas:
                                                partida[x][y - 1]['brillo'] = False
                                            if x - 1 >= 0:
                                                partida[x][y - 1]['brillo'] = False
                                            if y < self.num_celdas:
                                                partida[x][y]['brillo'] = False
                                            if y - 2 >= 0:
                                                partida[x][y - 2]['brillo'] = False
                                            self.tablero = partida
                                            logging.info(f'El jugador encontró el oro. El tablero queda así:\n{self.tablero_sorteo}')
                                            print('\nTENGO EL ORO!! HE DE VOLVER VIVO A LA CASILLA DE SALIDA!!!!.\n')
                                            
                                            
                                            print(sorteo)
                                            self.mover_jugador(self.tablero, self.tablero_sorteo, self.direccion)
                                        
                                        else:
                                            logging.info(f'El jugador avanza una casilla. El tablero queda así:\n{self.tablero_sorteo}')
                                            print("avanzo una casilla...")
                                            break
                                        

                                elif keys[0] == 'S':
                                    self.lanzar_flecha(self.tablero, self.tablero_sorteo, x, y)

                                elif keys[0] == 'A': # izquierda A
                                    print('\nHas girado 90º a la izquierda. Vas en dirección ESTE')
                                    self.direccion = keys[1]
                                    break
                                elif keys[0] == 'D': # derecha D
                                    print('\nHas girado 90º a la derecha. Vas en dirección OESTE')
                                    self.direccion = keys[1]
                                    break

                                elif keys[0] == 'Q':
                                    self.casilla_actual = self.get_casilla(self.tablero)
                                    salir = self.salir_partida(self.casilla_salida, self.casilla_actual)
                                    if salir:
                                        self.movimiento = False
                                        self.hay_partida = False
                                        break
                                    else:
                                        break
                            
                            except TypeError:
                                break
                            except Exception as e:
                                print('\nAlgo ha ocurrido\n')
                                traceback.print_exc()
                                return

                        elif self.direccion == 'E':
                            try:
                                print(f'Voy en direccion ESTE')
                                keys = self.check_accion()
                                if keys[0] == 'W':
                                    if (x + 1) >= self.num_celdas:
                                        print('\nBOOM!! CHOCASTE CONTRA UN MURO! PRUEBA EN OTRA DIRECCIÓN.')
                                        break
                                    else:
                                        partida[x + 1][y]['jugador'] = True
                                        partida[x + 1][y]['flechas'] = self.flechas
                                        partida[x][y]['jugador'] = False
                                        partida[x][y]['flechas'] = 0

                                        sorteo[x + 1][y] = 1
                                        sorteo[x][y] = 0

                                        self.tablero = partida
                                        self.tablero_sorteo = sorteo

                                        if partida[x + 1][y]['wumpus']:
                                            print('\nHAS SIDO ELIMINADO POR EL WUMPUS.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador fue eliminado por el Wumpus:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x + 1][y]['pozo']:
                                            print('\nHAS CAIDO EN UN POZO Y HAS SIDO ELIMINADO.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador calló en un pozo y quedó eliminado:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x + 1][y]['oro']:
                                            partida[x + 1][y]['oro'] = False
                                            partida[x + 1][y]['tiene_el_oro'] = True
                                            # actualizo las celdas del brillo
                                            if x + 2 < self.num_celdas:
                                                partida[x + 2][y]['brillo'] = False
                                            if x >= 0:
                                                partida[x][y]['brillo'] = False
                                            if y + 1 < self.num_celdas:
                                                partida[x + 1][y + 1]['brillo'] = False
                                            if y - 1 >= 0:
                                                partida[x + 1][y - 1]['brillo'] = False
                                            self.tablero = partida
                                            logging.info(f'El jugador encontró el oro. El tablero queda así:\n{self.tablero_sorteo}')
                                            print('\nTENGO EL ORO!! HE DE VOLVER VIVO A LA CASILLA DE SALIDA!!!!.\n')
                                            
                                            break
                                        else:
                                            logging.info(f'El jugador avanza una casilla. El tablero queda así:\n{self.tablero_sorteo}')
                                            print("avanzo una casilla...")
                                            break
                                        

                                elif keys[0] == 'S':
                                    self.lanzar_flecha(self.tablero, self.tablero_sorteo, x, y)

                                elif keys[0] == 'A':
                                    print('\nHas girado 90º a la derecha. Vas en dirección NORTE')
                                    self.direccion = keys[1]
                                    break
                                elif keys[0] == 'D':
                                    print('\nHas girado 90º a la izquierda. Vas en dirección SUR')
                                    self.direccion = keys[1]
                                    break
                                
                                elif keys[0] == 'Q':
                                    self.casilla_actual = self.get_casilla(self.tablero)
                                    salir = self.salir_partida(self.casilla_salida, self.casilla_actual)
                                    if salir:
                                        self.movimiento = False
                                        self.hay_partida = False
                                        break
                                    else:
                                        break
                            
                            except TypeError:
                                break
                            except Exception as e:
                                print('\nAlgo ha ocurrido\n')
                                traceback.print_exc()
                                break

                        elif self.direccion == 'O':
                            try:
                                print(f'Voy en direccion OESTE')
                                keys = self.check_accion()
                                if keys[0] == 'W':
                                    if (x - 1) < 0:
                                        print('\nBOOM!! CHOCASTE CONTRA UN MURO! PRUEBA EN OTRA DIRECCIÓN.')
                                        break
                                    else:
                                        partida[x - 1][y]['jugador'] = True
                                        partida[x - 1][y]['flechas'] = self.flechas
                                        partida[x][y]['jugador'] = False
                                        partida[x][y]['flechas'] = 0

                                        sorteo[x - 1][y] = 1
                                        sorteo[x][y] = 0

                                        self.tablero = partida
                                        self.tablero_sorteo = sorteo

                                        if partida[x - 1][y]['wumpus']:
                                            print('\nHAS SIDO ELIMINADO POR EL WUMPUS.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador fue eliminado por el Wumpus:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x - 1][y]['pozo']:
                                            print('\nHAS CAIDO EN UN POZO Y HAS SIDO ELIMINADO.\n ----- G A M E  O V E R -----')
                                            logging.info(f'El jugador calló en un pozo y quedó eliminado:\n{self.tablero_sorteo}')
                                            self.movimiento = False
                                            self.hay_partida = False
                                            break
                                        elif partida[x - 1][y]['oro']:
                                            partida[x - 1][y]['oro'] = False
                                            partida[x - 1][y]['tiene_el_oro'] = True
                                            # actualizo las celdas del brillo
                                            if x - 2 >= 0:
                                                partida[x - 2][y]['brillo'] = False
                                            if x < self.num_celdas:
                                                partida[x][y]['brillo'] = False
                                            if y + 1 < self.num_celdas:
                                                partida[x - 1][y + 1]['brillo'] = False
                                            if y - 1 >= 0:
                                                partida[x - 1][y - 1]['brillo'] = False
                                            self.tablero = partida
                                            logging.info(f'El jugador encontró el oro. El tablero queda así:\n{self.tablero_sorteo}')
                                            print('\nTENGO EL ORO!! HE DE VOLVER VIVO A LA CASILLA DE SALIDA!!!!.\n')
                                            break
                                        else:
                                            logging.info(f'El jugador avanza una casilla. El tablero queda así:\n{self.tablero_sorteo}')
                                            print("avanzo una casilla...")
                                            break
                                        
                                    
                                elif keys[0] == 'S':
                                    self.lanzar_flecha(self.tablero, self.tablero_sorteo, x, y)

                                elif keys[0] == 'A':
                                    print('\nHas girado 90º a la derecha. Vas en dirección SUR')
                                    self.direccion = keys[1]
                                    break

                                elif keys[0] == 'D':
                                    print('\nHas girado 90º a la izquierda. Vas en dirección NORTE')
                                    self.direccion = keys[1]
                                    break
                                
                                elif keys[0] == 'Q':
                                    self.casilla_actual = self.get_casilla(self.tablero)
                                    salir = self.salir_partida(self.casilla_salida, self.casilla_actual)
                                    if salir:
                                        self.movimiento = False
                                        self.hay_partida = False
                                        break
                                    else:
                                        break
                            except TypeError:
                                break
                            except Exception as e:
                                print('\nAlgo ha ocurrido\n')
                                traceback.print_exc()
                                break
    
    # LANZAR FLECHAS
    def lanzar_flecha(self, partida, sorteo, x, y):
        if self.flechas > 0:
            if self.direccion == 'N':
                if partida[x][y]['flechas'] > 0:
                    for i in range(0, self.num_celdas):
                        if (y + i) < self.num_celdas:
                            if partida[x][y + i]['wumpus']:
                                partida[x][y + i]['wumpus'] = False
                                self.flechas -= 1
                                partida[x][y]['flechas'] = self.flechas
                                sorteo[x][y + i] = 0
                                self.tablero = partida
                                self.tablero_sorteo = sorteo
                                # actualizo las celdas del olor
                                if x + 1 < self.num_celdas:
                                    partida[x + 1][y]['olor'] = False
                                    self.tablero = partida
                                if x - 1 >= 0:
                                    partida[x - 1][y]['olor'] = False
                                    self.tablero = partida
                                if y + 1 < self.num_celdas:
                                    partida[x][y + 1]['olor'] = False
                                    self.tablero = partida
                                if y - 1 >= 0:
                                    partida[x][y - 1]['olor'] = False
                                    self.tablero = partida
                                
                                print('\nAWWWW!!! ENHORABUENA, HAS MATADO AL WUMPUS!. ENCUENTRA EL ORO Y VE A LA SALIDA!!!')    
                                self.movimiento = False
                        else:
                            self.flechas -= 1
                            partida[x][y]['flechas'] = self.flechas
                            print(f'\nFallaste el tiro! te quedan {self.flechas} flechas')
                            self.movimiento = False
        

            elif self.direccion == 'S':
                if partida[x][y]['flechas'] > 0:
                    for i in range(0, self.num_celdas):
                        if (y - i) >= 0:
                            if partida[x][y - i]['wumpus']:
                                partida[x][y - i]['wumpus'] = False
                                self.flechas -= 1
                                partida[x][y]['flechas'] = self.flechas
                                sorteo[x][y - i] = 0
                                self.tablero = partida
                                self.tablero_sorteo = sorteo
                                # actualizo las celdas del olor
                                if x + 1 < self.num_celdas:
                                    partida[x + 1][y]['olor'] = False
                                    self.tablero = partida
                                if x - 1 >= 0:
                                    partida[x - 1][y]['olor'] = False
                                    self.tablero = partida
                                if y + 1 < self.num_celdas:
                                    partida[x][y + 1]['olor'] = False
                                    self.tablero = partida
                                if y - 1 >= 0:
                                    partida[x][y - 1]['olor'] = False
                                    self.tablero = partida
                                
                                print('\nAWWWW!!! ENHORABUENA, HAS MATADO AL WUMPUS!. ENCUENTRA EL ORO Y VE A LA SALIDA!!!')
                                
                                self.movimiento = False
                        else:
                            self.flechas -= 1
                            partida[x][y]['flechas'] = self.flechas
                            print(f'\nFallaste el tiro! te quedan {self.flechas} flechas')
                            self.movimiento = False
            elif self.direccion == 'E':
                if partida[x][y]['flechas'] > 0:
                    for i in range(0, self.num_celdas):
                        if (x + i) < self.num_celdas:
                            if partida[x + i][y]['wumpus']:
                                partida[x + i][y]['wumpus'] = False
                                self.flechas -= 1
                                partida[x][y]['flechas'] = self.flechas
                                sorteo[x + i][y] = 0
                                self.tablero = partida
                                self.tablero_sorteo = sorteo
                                # actualizo las celdas del olor
                                if x + 1 < self.num_celdas:
                                    partida[x + 1][y]['olor'] = False
                                    self.tablero = partida
                                if x - 1 >= 0:
                                    partida[x - 1][y]['olor'] = False
                                    self.tablero = partida
                                if y + 1 < self.num_celdas:
                                    partida[x][y + 1]['olor'] = False
                                    self.tablero = partida
                                if y - 1 >= 0:
                                    partida[x][y - 1]['olor'] = False
                                    self.tablero = partida
                                
                                print('\nAWWWW!!! ENHORABUENA, HAS MATADO AL WUMPUS!. ENCUENTRA EL ORO Y VE A LA SALIDA!!!')
                                self.movimiento = False
                        else:
                            self.flechas -= 1
                            partida[x][y]['flechas'] = self.flechas
                            print(f'\nFallaste el tiro! te quedan {self.flechas} flechas')
                            self.movimiento = False
            elif self.direccion == 'O':
                if partida[x][y]['flechas'] > 0:
                    for i in range(0, self.num_celdas):
                        if (x - i) >= 0:
                            if partida[x - i][y]['wumpus']:
                                partida[x - i][y]['wumpus'] = False
                                self.flechas -= 1
                                partida[x][y]['flechas'] = self.flechas
                                sorteo[x - i][y] = 0
                                self.tablero = partida
                                self.tablero_sorteo = sorteo
                                # actualizo las celdas del olor
                                if x + 1 < self.num_celdas:
                                    partida[x + 1][y]['olor'] = False
                                    self.tablero = partida
                                if x - 1 >= 0:
                                    partida[x - 1][y]['olor'] = False
                                    self.tablero = partida
                                if y + 1 < self.num_celdas:
                                    partida[x][y + 1]['olor'] = False
                                    self.tablero = partida
                                if y - 1 >= 0:
                                    partida[x][y - 1]['olor'] = False
                                    self.tablero = partida
                                
                                
                                print('\nAWWWW!!! ENHORABUENA, HAS MATADO AL WUMPUS!. ENCUENTRA EL ORO Y VE A LA SALIDA!!!')
                                self.movimiento = False
                        else:
                            self.flechas -= 1
                            partida[x][y]['flechas'] = self.flechas
                            print(f'\nFallaste el tiro! te quedan {self.flechas} flechas')
                            self.movimiento = False
        else:
            print('\nNO TIENES MÁS FLECHAS!')
            self.movimiento = False
        
        

    def get_casilla(self, partida):
        casilla = None
        for (x, y), arr in np.ndenumerate(partida):
            if arr['jugador']: # si es la casilla del jugador
                casilla = [x, y]
        return casilla


    def salir_partida(self, casilla_salida, casilla_actual):
        if casilla_salida == casilla_actual:
            print('\nENHORABUENA!!! HAS SOBREVIVIDO AL WUMPUS!')
            logging.info(f'El jugador ha sobrevivido al Wumpus. Este es el mapa final: {self.tablero}')
            
            return True
        else:
            print('\nAQUÍ NO HAY SALIDA... VE A LA CASILLA DE SALIDA')
            return False


    def es_iterable(self, matriz):
        # if matriz.any():
        try:
            for fila in matriz:
                try:
                    object_iterator = iter(matriz[0])
                    return True
                except TypeError:
                    return False
                else:
                    return True
        except TypeError: # NoneType
            return False

partida = Partida()