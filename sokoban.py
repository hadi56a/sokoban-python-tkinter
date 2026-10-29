# -*- coding: utf-8 -*-
"""
@author: Alain Plantec

Voici un skelette possible.
Vous devez programmez les classes contenues dans ce squelette.
Les fonctions et leurs paramètres ainsi que les variables contenues dans le classes
ont du sens par rapport à une version programmée pour la préparation du projet.
Votre version sera forcément différente.
Donc, vous pouvez ajouter/retirer des variables et/ou des fonctions et/ou des paramètres.

"""
try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox

from sokobanXSBLevels import *
from enum import Enum

# Pour la sauvegarde des fichiers
import json


"""
Direction :
    Utile pour gérer le calcul des positions pour les mouvements
"""
class Direction(Enum):
    Up = 1
    Down = 2
    Left = 3
    Right = 4

"""
Position :
    - stockage de coordonnées x et y,
    - vérification de x et y par rapport à une matrice
    - calcule de position relative à partir d'un offset (un décalage) et une direction 
"""
class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Position(' + str(self.x) + ',' + str(self.y) + str(')') 

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    # retoune la position vers la direction #direction en tenant compte de l'offset
    # Position(3,4).positionTowards(Direction.Right, 2) == Position(5,4)
    def positionTowards(self, direction, offset):
        """
        Fonction à compléter : fonction qui renvoie la position après déplacement
        """
        if direction == Direction.Up:
            return Position(self.x, self.y - offset)
        elif direction == Direction.Down:
            return Position(self.x, self.y + offset)
        elif direction == Direction.Left:
            return Position(self.x - offset, self.y)
        elif direction == Direction.Right:
            return Position(self.x + offset, self.y)

    # Retourne True si les coordonnées sont valides dans le wharehouse
    def isValidInWharehouse(self, wharehouse):
        return wharehouse.isPositionValid(self)

    # Convertit le receveur en une position correspondante dans un Canvas
    def asCanvasPositionIn(self, elem):
        lx = self.getX() * elem.getWidth() 
        ly = self.getY() * elem.getHeight()
        return Position(lx, ly)

"""
WharehousePlan : Plan de l'entrepot pour stocker les éléments.
    Les éléments sont stockés dans une matrice (#rawMatrix)
"""
class WharehousePlan(object):
    def __init__(self):
        # la matrice d'Elements
        self.rawMatrix = []

    def appendRow(self, row):
        """
        Fonction à compléter : fonction qui rajoute une ligne dans la matrice
        """
        self.rawMatrix.append(row)
 
    def at(self, position):
        """
        Fonction à compléter : fonction qui renvoie l'élément à la position entrée en argument
        """
        return self.rawMatrix[position.getY()][position.getX()]
    
    def atPut(self, position, elem):
        """
        Fonction à compléter : fonction qui place un élément placé en argument dans la matrice
        """
        self.rawMatrix[position.getY()][position.getX()] = elem
        
    def isPositionValid(self, position):
        """
        Fonction à compléter : fonction qui vérifie si la position est valide
        """
        if(0 <= position.getY() < len(self.rawMatrix) and 0 <= position.getX() < len(self.rawMatrix[position.getY()])):
            return True
        else:
            return False

    def hasFreePlaceAt(self, position):
        return self.at(position).isFreePlace()

    def asXsbMatrix(self):
        return xsbMatrix(self.rawMatrix)
    
"""
Floor :
    Représente une case vide de la matrice
    (pas de None dans la matrice)
"""
class Floor(object):
    def __init__(self):
        None
    def isMovable(self):
        return False
    def canBeCovered(self):
        return True
    def xsbChar(self):
        return ' '
    def isFreePlace(self):
        return True

"""
Goal :
    Représente une localisation à recouvrir d'un BOX (objectif du jeu).
    Le déménageur doit parvenir à couvrir toutes ces cellules à partir des caisses.
    Un Goal est static, il est toujours déssiné en dessous :
        Le zOrder est assuré par le tag du create_image (tag='static')
        et self.canvas.tag_raise("movable","static") dans Level
"""
class Goal(object):
    def __init__(self, canvas, position):
        """
        Fonction à compléter : fonction d'initialisation des Goals
        """
        self.canvas = canvas
        self.position = position
        
        self.height = 64
        self.width = 64
        
        # Image du Goal
        self.image = tk.PhotoImage(file='goal.png')
        self.canvas.create_image(self.position.getX()*64,self.position.getY()*64,image=self.image, anchor=tk.NW, tag="static")

    def isMovable(self):
        return False

    def getHeight(self):
        return self.height
    
    def getWidth(self):
        return self.width

    def canBeCovered(self):
        return True
        
    def xsbChar(self):
        return '.'

    def isFreePlace(self):
        return False

"""
Wall : pour délimiter les murs
    Le déménageur ne peut pas traverser un mur.
    Un Wall est static, il est toujours déssiné en dessous :
        Le zOrder est assuré par le tag du create_image (tag='static')
        et self.canvas.tag_raise("movable","static") dans Level
"""
class Wall(object):
    def __init__(self, canvas, position):
        """
        Fonction à compléter : fonction d'initialisation des Walls
        """
        self.canvas = canvas
        self.position = position
        
        self.height = 64
        self.width = 64
        
        # Image du Wall
        self.image = tk.PhotoImage(file='wall.png')
        self.canvas.create_image(self.position.getX()*64,self.position.getY()*64,image=self.image, anchor=tk.NW, tag="static")

    def getHeight(self):
        return self.height
    
    def getWidth(self):
        return self.width

    def isMovable(self):
        return False

    def canBeCovered(self):
        return False

    def xsbChar(self):
        return '#'

    def isFreePlace(self):
        return False

"""
Box : Caisse à déplacer par le déménageur.
    Etant donné qu'une caisse doit être déplacé, le canvas et la matrice sont necessaires pour
    reconstruire l'image et mettre en oeuvre sont déplacement (dans le canvas et dans la matrice)
    Un Box est "movable", il est toujours déssiné au dessus des objets "static" :
        Le zOrder est assuré par le tag du create_image (tag='movable')
        et self.canvas.tag_raise("movable","static") dans Level
    Un Box est représenté differemment (image différente) suivant qu'il se situe sur un emplacement marqué par un Goal ou non.
 """
class Box(object):
    def __init__(self, canvas, wharehouse, position, onGoal):
        """
        Fonction à compléter : fonction d'initialisation des Boxs
        """
        self.canvas = canvas
        self.wharehouse = wharehouse
        self.position = position
        self.onGoal = onGoal
        
        # Variable pour la gestion du score
        self.valide_goal = False
        
        # Variables de l'animation
        self.animation = None
        self.animation_job = None
        
        self.height = 64
        self.width = 64
        
        # Image de la Box
        self.image = tk.PhotoImage(file='box.png')
        self.image_onGoal = tk.PhotoImage(file='boxOnTarget.png')
        
        # Si la Box est sur un Goal, l'image change et l'élément qui est en dessous aussi
        if self.onGoal == True:
            self.boxId = self.canvas.create_image(self.position.getX()*64,self.position.getY()*64,image=self.image_onGoal, anchor=tk.NW, tag="movable")
            self.under = Goal(self.canvas, self.position)
        else:
            self.boxId = self.canvas.create_image(self.position.getX()*64,self.position.getY()*64,image=self.image, anchor=tk.NW, tag="movable")
            self.under = Floor()

    def getHeight(self):
        return self.height
    
    def getWidth(self):
        return self.width

    def isMovable(self):
        return True

    def canBeCovered(self):
        return False

    def moveTowards(self, direction):
        """
        Fonction à compléter : fonction qui permet le déplacement d'une Box
        """
        # Nouvelle position
        nouvelle_position = self.position.positionTowards(direction,1)
            
        # On remet l'élément qui était en dessous à la position
        self.wharehouse.atPut(self.position, self.under)
        # L'élément en dessous devient l'élément qui est à la position ou on veut aller
        self.under = self.wharehouse.at(nouvelle_position)
        
        # On vérifie si l'élément qui est en dessous est un Goal
        if type(self.under) == Goal:
            self.onGoal = True
            self.canvas.delete(self.boxId)
            self.boxId = self.canvas.create_image(nouvelle_position.getX() * 64, nouvelle_position.getY() * 64, image=self.image_onGoal, anchor=tk.NW, tag="movable")
            self.startGoalCoveredAnimation()
        elif type(self.under) == Floor:
            self.onGoal = False
            self.canvas.delete(self.boxId)
            self.boxId = self.canvas.create_image(nouvelle_position.getX() * 64, nouvelle_position.getY() * 64, image=self.image, anchor=tk.NW, tag="movable")
        
        # On place la Box à la nouvelle position
        self.wharehouse.atPut(nouvelle_position, self)
        
        # La position de la Box devient la nouvelle position
        self.position = nouvelle_position
 
    def xsbChar(self):
        if self.under.isFreePlace(): return '$'
        else: return '*'

    def isFreePlace(self):
        return False

    def startGoalCoveredAnimation(self):
        """
        Fonction à compléter : fonction lance l'animation de la Box
        """
        # Si une animation est déjà en cours, on l'arrête avant d'en lancer une nouvelle
        if self.animation_job != None:
            self.canvas.after_cancel(self.animation_job)
            self.animation_job = None
        self.cleanUpAnimation()
        
        # Initialisation des variables d'animation
        self.pas_animation = 6
        self.pas_actuelle = 0
        self.rayon = 0
        
        self.goalCoveredAnimation()
 
    def cleanUpAnimation(self):
        """
        Fonction à compléter : fonction qui stop l'animation de la Box
        """
        if self.animation != None:
            self.canvas.delete(self.animation)
            self.animation = None
  
    def goalCoveredAnimation(self):
        """
        Fonction à compléter : fonction réalise l'animation de la Box
        """
        # Coordonnées de l'animation
        x = self.position.getX() * 64 + 32
        y = self.position.getY() * 64 + 32
        
        # On supprime l'ancien cercle
        if self.animation != None:
            self.canvas.delete(self.animation)
        
        # On en créé un nouveau
        self.animation = self.canvas.create_oval(x - self.rayon, y - self.rayon, x + self.rayon, y + self.rayon, outline="yellow", width=1)
        
        # On augmente la pas et le rayon
        self.rayon += 5
        self.pas_actuelle += 1
        
        # Tant que la pas actuelle est inférieur au pas d'animation, on recommence
        if self.pas_actuelle < self.pas_animation:
            self.animation_job = self.canvas.after(50,self.goalCoveredAnimation)
        # Sinon, on arrête l'animation
        else:
            self.animation_job = None
            self.cleanUpAnimation()

 
"""
Mover : C'est  le déménageur.
    La classe Mover met en oeuvre la logique du jeu dans #canMove et #moveTowards.
    Etant donné qu'un Mover se déplace, le canvas et la matrice sont necessaires pour
    reconstruire l'image et mettre en oeuvre sont déplacement (dans le canvas et dans la matrice)
    Un Mover est "movable", il est toujours déssiné au dessus des objets "static" :
        Le zOrder est assuré par le tag du create_image (tag='movable')
        et self.canvas.tag_raise("movable","static") dans Level
    Un Box est représenté differemment (image différente) suivant la direction de déplacement (même si le dépplacement s'avère impossible).
"""
class Mover(object):
    def __init__(self, canvas, wharehouse, position, onGoal):
        """
        Fonction à compléter : fonction d'intialisation du Mover
        """
        self.canvas = canvas
        self.wharehouse = wharehouse
        self.position = position
        self.onGoal = onGoal

        self.height = 64
        self.width = 64

        # Variables de l'animation
        self.animation = None
        self.animation_job = None

        # Image du Mover
        self.image = tk.PhotoImage(file='playerDown.png')
        self.playerId = self.canvas.create_image(self.position.getX()*64,self.position.getY()*64,image=self.image, anchor=tk.NW, tag="movable")
        
        # On calcul l'élement qui est en dessous du Mover
        if self.onGoal == True:
            self.under = Goal(self.canvas, self.position)
        else:
            self.under = Floor()

    def getHeight(self):
        return self.height
    
    def getWidth(self):
        return self.width

    def isMoveable(self):
        return True

    def moveInCanvas(self, direction):
        """
        Fonction à compléter : fonction qui permet de déplacer l'image du joueur dans le canvas
        """
        # Calcul de la nouvelle position
        nouvelle_position = self.position.positionTowards(direction, 1)
        # On supprime l'ancienne image
        self.canvas.delete(self.playerId)
        # On en créé une nouvelle à la nouvelle position
        self.playerId = self.canvas.create_image(nouvelle_position.getX() * 64, nouvelle_position.getY() * 64, image=self.image, anchor=tk.NW, tag="movable")
        # La positrion actuelle devient la nouvelle position
        self.position = nouvelle_position

    """
        Retourne True si le Mover peut se déplacer dans la direction demandée.
        Le calcul necessite de voir l'élément adjacent mais aussi l'élément suivant (offset de 2)
    """
    def canMove(self, direction):
        """
        Fonction à compléter : fonction qui vérifie les possibilités de déplacement du Mover et des Boxs
        """
        # On défini la prochaine position et l'élément qui est à cette prochaine position
        prochaine_position = self.position.positionTowards(direction,1)
        prochain_element = self.wharehouse.at(prochaine_position)
        
        # Si l'élément est un Floor on peut y aller
        if type(prochain_element) == Floor:
            return True
    
        # Si l'élément est une Box, on regarde la position après la Box et l'élément qui s'y trouve
        if type(prochain_element) == Box:
            prochaine_prochaine_position = self.position.positionTowards(direction, 2)
            prochain_prochain_element = self.wharehouse.at(prochaine_prochaine_position)
    
            # Si l'élément après la Box est un Floor, on peut y aller
            if type(prochain_prochain_element) == Floor or type(prochain_prochain_element) == Goal:
                return True
    
        # Si l'élément est un Goal, on peut y aller
        if type(prochain_element) == Goal:
            self.onGoal = True
            return True
    
        # Sinon, on peut pas y aller
        self.onGoal = False
        return False

    """
        Pour le déplacement, il faut penser à déplacer éventuellemnt le Box et ensuite déplacer le Mover
    """
    def moveTowards(self, direction):
        """
        Fonction à compléter : fonction qui réalise le déplacement du Mover et des Boxs dans le wharehouse
        """
        # On défini la prochaine position et l'élément qui est à cette prochaine position
        prochaine_position = self.position.positionTowards(direction,1)
        prochain_element = self.wharehouse.at(prochaine_position)
    
        # Si l'élément est une Box, on appelle la fonction moveTowards de la Box qui va se charger du déplacement
        if type(prochain_element) == Box:
            prochain_element.moveTowards(direction)

        # On met à la position actuelle l'élément qui y était avant
        self.wharehouse.atPut(self.position, self.under)
        # On sauvegarde l'élément qui est à la prochaine position
        self.under = self.wharehouse.at(prochaine_position)
        # On déplace le Mover
        self.wharehouse.atPut(prochaine_position, self)
        
        # On appel la fonction moveInCanvas qui va déplacer l'image du Mover
        self.moveInCanvas(direction)
        
        # La position actuelle du Mover devient la prochaine psoition
        self.position = prochaine_position

    """
        Le Mover est représenté differemment suivant la direction de déplacement
    """
    def setupImageForDirection(self, dir):
        """
        Fonction à compléter : fonction qui modifie l'image du Mover en fonction de la direction
        """
        if(dir == Direction.Up):
            self.image = tk.PhotoImage(file='playerUp.png')
        elif(dir == Direction.Down):
            self.image = tk.PhotoImage(file='playerDown.png')
        elif(dir == Direction.Left):
            self.image = tk.PhotoImage(file='playerLeft.png')
        elif(dir == Direction.Right):
            self.image = tk.PhotoImage(file='playerRight.png')

    """
        Pour le déplacement :
            - image changée en fonction de la direction
            - si on ne peut pas se déplacer dans cette direction -> abandon
            - sinon, bin le Mover est déplacé
    """
    def push(self, direction):
        self.setupImageForDirection(direction)
        if not self.canMove(direction):
            self.startImpossiblePushAnimation()
            return
        self.moveTowards(direction)

    def xsbChar(self):
        if self.under.isFreePlace(): return '@'
        else: return '+'

    def isFreePlace(self):
        return False

    def startImpossiblePushAnimation(self):
        """
        Fonction à compléter : fonction qui lance l'animation du Mover
        """
        # Si une animation est déjà en cours (touches appuyées rapidement), on l'arrête
        if self.animation_job != None:
            self.canvas.after_cancel(self.animation_job)
            self.animation_job = None
        self.cleanUpAnimation()
        
        # On définis les variables d'animation
        self.pas_animation = 6
        self.pas_actuelle = 0
        self.rayon = 0
        
        # On remplace l'image du joueur (nouvelle direction) sans laisser l'ancienne
        self.canvas.delete(self.playerId)
        self.playerId = self.canvas.create_image(self.position.getX() * 64, self.position.getY() * 64, image=self.image, anchor=tk.NW, tag="movable")
        
        self.impossiblePushAnimation()

    def cleanUpAnimation(self):
        """
        Fonction à compléter : fonction stop l'animation du Mover
        """
        if self.animation != None:
            self.canvas.delete(self.animation)
            self.animation = None

    def impossiblePushAnimation(self):
        """
        Fonction à compléter : fonction réalise l'animation du Mover
        """
        # Position de l'animation
        x = self.position.getX() * 64 + 32
        y = self.position.getY() * 64 + 32
        
        # On supprime l'ancien cercle
        if self.animation != None:
            self.canvas.delete(self.animation)
        
        # On créé un nouveau cercle
        self.animation = self.canvas.create_oval(x - self.rayon, y - self.rayon, x + self.rayon, y + self.rayon, outline="red", width=1)
        
        # On modifie le rayon et la pas actuelle
        self.rayon += 5
        self.pas_actuelle += 1
        
        # On répète tout cela tant que le pas actuelle est inférieur au pas de l'animation
        if self.pas_actuelle < self.pas_animation:
            self.animation_job = self.canvas.after(50,self.impossiblePushAnimation)
        else:
            self.animation_job = None
            self.cleanUpAnimation()

"""
    Le jeux avec tout ce qu'il faut pour dessiner et stocker/gérer la matrice d'éléments
    
"""
class Level(object):
    def __init__(self, root, xsbMatrix, joueur, liste_scores):
        self.root = root
        self.wharehouse = WharehousePlan()
        
        # Initialisation du score, du joueur et de la liste des scores
        self.score = 500
        self.joueur = joueur
        self.liste_scores = liste_scores

        # calcul des dimensions de la matrice
        nbrows = len(xsbMatrix)
        nbcolumns = 0

        for line in xsbMatrix:
            nbc = len(line)
            if nbc > nbcolumns:
                nbcolumns = nbc

        self.height = nbrows * 64 
        self.width = nbcolumns * 64 
 
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="gray")
        self.canvas.grid()

        self.initWharehouseFromXsb(xsbMatrix)
        self.root.bind("<Key>", self.keypressed)
        
        # On met à jour le score
        self.majScore()
        
        # Création du chronomètre
        self.chrono = Chrono(self.canvas, 90, self.finPartie)
        # On démarre le chrono au lancement du niveau
        self.chrono.start()

    def initWharehouseFromXsb(self,xsbMatrix):
        """
        Fonction à compléter : fonction qui place (initialise) dans le wharehouse tous les éléments en fonction de leurs symboles
        """
        # legend :
        #   '#' = wall,  '$' = box, '.' = goal, '*' = box on goal, '@' = mover, '+' = mover on goal, '-' = floor, ' ' = floor
        self.staticMatrix = []
        self.movableMatrix = []
        for lineIdx in range(len(xsbMatrix)):
            self.staticMatrix.append([])
            self.movableMatrix.append([])
            for elemIdx in range(len(xsbMatrix[lineIdx])):
                self.staticMatrix[lineIdx].append(None)
                self.movableMatrix[lineIdx].append(None)
        
        y = 0
        for lineIdx in range(len(xsbMatrix)):
            x = 0
            ligne = []
            for elemIdx in range(len(xsbMatrix[lineIdx])):
                e = xsbMatrix[lineIdx][elemIdx]
                if e == '#':
                    element = Wall(self.canvas,Position(x,y))
                    ligne.append(element)
                    self.staticMatrix[y][x] = element.image
                elif e == '@':
                    element = Mover(self.canvas, self.wharehouse, Position(x,y), False)
                    ligne.append(element)
                    self.player = element
                    self.movableMatrix[y][x] = self.player.image
                elif e == '.':
                    element = Goal(self.canvas, Position(x,y))
                    ligne.append(element)
                    self.staticMatrix[y][x] = element.image
                elif e == '$':
                    element = Box(self.canvas, self.wharehouse, Position(x,y), False)
                    ligne.append(element)
                    self.movableMatrix[y][x] = element.image
                elif e == '*':
                    element = Box(self.canvas, self.wharehouse, Position(x,y), True)
                    ligne.append(element)
                    self.staticMatrix[y][x] = element.image_onGoal
                elif e == '+':
                    element = Mover(self.canvas, self.wharehouse, Position(x,y), True)
                    ligne.append(element)
                    self.player = element
                    self.movableMatrix[y][x] = self.player.image
                elif e == '-':
                    element = Floor()
                    ligne.append(element)
                elif e == ' ':
                    element = Floor()
                    ligne.append(element)
                
                x = x + 1
            y = y + 1
            x = 0
            self.wharehouse.appendRow(ligne)
        self.canvas.tag_raise("movable","static")
        
    def keypressed(self, event):
        """
        Fonction à compléter : fonction qui permet d'intéragir dans le jeu avec les flèches du clavier
        """
        # Eviter les erreurs au niveau des champs quand on relance une partie
        if self.canvas is None:
            return
        # On ignore les touches qui ne sont pas des flèches
        if event.keysym not in ('Up', 'Down', 'Left', 'Right'):
            return
        
        # Quand on appuit sur une touche, on lance la fonction push du Mover
        if event.keysym == 'Up':
            self.player.push(Direction.Up)
        elif event.keysym == 'Down':
            self.player.push(Direction.Down)
        elif event.keysym == 'Left':
            self.player.push(Direction.Left)
        elif event.keysym == 'Right':
            self.player.push(Direction.Right)
        
        # On modifie le score
        self.score -= 1
        # On vérifie si une Box est sur un Goal
        self.verifGoal()
        # On met à jour le score
        self.majScore()

        # On vérifie si les Boxs sont toutes sur des Goals
        if self.verifFin() == True:
            self.finPartie()


    def majScore(self):
        """
        Fonction qui met à jour l'affichage du score à chaque movement du Mover
        """
        self.canvas.delete("score")
        score_text = "Score : " + str(self.score)
        self.canvas.create_text(50, 50, text=score_text, fill="black", tag="score")
        
    def verifGoal(self):
        """
        Fonction qui vérifie si une Box est sur un Goal
        """
        # On parcours la matrice
        for y in range(len(self.wharehouse.rawMatrix)):
            for x in range(len(self.wharehouse.rawMatrix[y])):
                element = self.wharehouse.rawMatrix[y][x]
                # Si l'élément est une Box
                if type(element) == Box: 
                    # Si la Box est sur un Goal et qu'elle na pas déjà été comptée
                    if element.onGoal == True and element.valide_goal == False:
                        self.score += 50
                        element.valide_goal = True
                    # Si elle n'est pas sur un Goal et qu'elle a déjà été comptée
                    elif element.onGoal == False and element.valide_goal == True:
                        self.score -= 50
                        element.valide_goal = False
        
    def verifFin(self):
        """
        Fonction qui vérifie si toutes les Boxs sont sur des Goals
        """
        # La partie est finie seulement si toutes les Boxs sont sur un Goal
        for y in range(len(self.wharehouse.rawMatrix)):
            for x in range(len(self.wharehouse.rawMatrix[y])):
                element = self.wharehouse.rawMatrix[y][x]
                if type(element) == Box and element.onGoal == False:
                    return False
        return True
    
    def finPartie(self):
        """
        Fonction qui met fin à la partie
        """
        # On créé un nouveau score
        score = Score(self.joueur, self.score)
        # On l'ajoute à la liste des scores
        self.liste_scores.ajout(score)
        self.liste_scores.toFile("scores.json")
        
        # On enlève le canvas
        self.canvas.destroy()
        self.canvas = None
        self.level = None
        # On appel la classe Panneau qui nous ramène au menu
        self.panneau = Panneau(self.root)

"""
    Classe qui gère la création d'un score
"""
class Score(object):
    def __init__(self, joueur, score):
        self.joueur = joueur
        self.score = score
    
    def __str__(self):
         return self.joueur + ',' + str(self.score)

"""
    Classe qui gère la liste des scores
"""
class ListeScores(object):
    def __init__(self):
        self.scores = []
    
    def ajout(self, score):
        """
        Fonction qui ajoute un score à la liste
        """
        self.scores.append(score)
    
    def __str__(self):
        chaine = str(self.scores[0])
        for e in self.scores[1:]:
            chaine = chaine + " / " + str(e)
        return chaine
    
    @classmethod
    def fromFile(cls, fichier):
        # On essaye d'ouvir le fichier
        try:
            # On ouvre le fichier
            f = open(fichier,"r")
            tmp = json.load(f)
            
            # Création d'une liste qui va contenir les scores présents dans le fichier
            liste = []
            for d in tmp:
                # On créé un score
                l = Score(d["Joueur"],d["Score"])
                # On l'ajoute dans la liste
                liste.append(l)
            scs = ListeScores()
            scs.scores = liste
            f.close();
            return scs
        # Sauf si le fichier est vide ou introuvable
        except (json.JSONDecodeError, FileNotFoundError):
            # Dans ce cas, on renvoi une instance vide de la classe ListeScore
            return cls()
    
    def toFile(self, fichier):
        f = open(fichier,"w")
        tmp = []
        for l in self.scores:
            d = {}
            d["Joueur"] = l.joueur
            d["Score"] = l.score
            tmp.append(d)
        json.dump(tmp,f)
        f.close()
    
"""
    Classe créé le panneau qui sert de menu
"""
class Panneau(object):
    def __init__(self, root):
        self.root = root
        
        # Titre du menu
        self.titre = tk.Label(self.root, text="Sokoban", font=("Arial", 40))
        self.titre.grid(row=0, column=0, columnspan=2)
        
        # Affichage des scores
        self.label_titre_score = tk.Label(self.root, text="Liste des Scores : ", font=("Arial", 20))
        self.label_titre_score.grid(row=1, column=0, columnspan=2)
        
        # Liste des scores
        self.liste_scores = ListeScores.fromFile("scores.json")
        
        # Si il n'y a pas de scores
        if not self.liste_scores.scores:
            scores_text = "Pas de scores"
        else:
            scores_text = str(self.liste_scores)
            
        self.label_scores = tk.Label(self.root, text=scores_text, font=("Arial", 14))
        self.label_scores.grid(row=2, column=0, columnspan=2)
        
        # Zone pour entrer le nom du joueur
        self.label_joueur = tk.Label(self.root, text="Nom : ")
        self.label_joueur.grid(row=3, column=0)
        self.nom_joueur = tk.Entry(self.root)
        self.nom_joueur.grid(row=3, column=1)
        
        # Zone pour entrer le niveau
        self.label_niveau = tk.Label(self.root, text="Niveau : ")
        self.label_niveau.grid(row=5, column=0)
        self.choix_niveau = tk.Entry(self.root)
        self.choix_niveau.grid(row=5, column=1)
        
        # Création du bouton qui lance la partie
        self.bouton_jouer = tk.Button(self.root, text="Jouer", command=self.jouer)
        self.bouton_jouer.grid(row=7, column=0)
        
        # Création du bouton quitter
        self.bouton_quitter = tk.Button(self.root, text="Quitter", command=self.quitter)
        self.bouton_quitter.grid(row=7, column=1)
        
        # Alertes des champs
        self.text_alert = tk.Label(self.root, text="Veuillez entrer un nom de joueur")
        self.text_alert2 = tk.Label(self.root, text="Veuillez choisir un niveau")


    def jouer(self):
        """
        Fonction qui lance le jeu si les deux champs sont remplis
        """
        # On récupère leurs valeurs
        joueur = self.nom_joueur.get()
        niveau = self.choix_niveau.get()
        
        # On vérifie si les champs sont vides
        if len(joueur) == 0:
            self.text_alert.grid(row=4, column=0, columnspan=2)
        elif len(niveau) == 0 or not niveau.isdigit() or int(niveau) >= len(SokobanXSBLevels):
            self.text_alert2.config(text="Veuillez choisir un niveau entre 0 et " + str(len(SokobanXSBLevels) - 1))
            self.text_alert2.grid(row=6, column=0, columnspan=2)
        else:
            # On supprime les éléments du canvas
            self.titre.destroy()
            self.label_titre_score.destroy()
            self.label_scores.destroy()
            self.nom_joueur.destroy()
            self.label_joueur.destroy()
            self.choix_niveau.destroy()
            self.label_niveau.destroy()
            self.bouton_jouer.destroy()
            self.bouton_quitter.destroy()
            self.text_alert.destroy()
            self.text_alert2.destroy()
            # On lance le jeu
            print('Sokoban: ' + str(len(SokobanXSBLevels)) + ' levels')
            self.level = Level(self.root, SokobanXSBLevels[int(niveau)], joueur, self.liste_scores)
    
    def quitter(self):
        self.root.destroy()

"""
    Classe créé le chronomètre du jeu
"""
class Chrono(object):
    def __init__(self, canvas, temps, fonction):
        self.canvas = canvas
        # Temps maximum
        self.temps = temps
        # Temps qu'il reste
        self.temps_restant = temps
        # Fonction qui est appelé quand le chronomètre se termine
        self.fonction = fonction
        # Etat du chronomètre
        self.actif = False
    
    def start(self):
        """
        Fonction qui lance le chronomètre
        """
        if self.actif == False:
            self.actif = True
            # On met à jour le chronomètre
            self.majChrono()
    
    def majChrono(self):
        """
        Fonction qui met à jour le chronomètre
        """
        if self.temps_restant > 0:
            # On réduit le temps
            self.temps_restant -= 1
            # On supprime l'ancien texte
            self.canvas.delete("chrono")
            # On en créé un nouveau avec la nouvelle valeur
            chrono_text = "Chrono : " + str(self.temps_restant) + " secondes"
            self.canvas.create_text(75, 30, text=chrono_text, fill="black", tag="chrono")
            # On relance cette fonction toute les 1000 ms soit 1s
            self.canvas.after(1000, self.majChrono)  
        # Sinon, on arrête le chronomètre
        else:
            self.stop()

    def stop(self):
        """
        Fonction qui arrête le chronomètre
        """
        self.actif = False
        # On appelle la fonction de fin
        self.fonction()

class Sokoban(object):
    '''
    Main Level class
    '''

    def __init__(self):
        self.root = tk.Tk()
        # La fenêtre peut être agrandie, le jeu reste centré
        self.root.resizable(True, True)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.title("Sokoban")
        
        self.panneau = Panneau(self.root)

    def play(self):
        self.root.mainloop()

if __name__ == "__main__":
    Sokoban().play()

