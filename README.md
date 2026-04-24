# Description du Jeux :
Le jeu commence par l'apparition d'un ou plusieurs points clignotants a des positions aléatoires (le nombre correspond au niveau de difficulté), que le joueur doit suivre en les dirigeant à l’aide d’un d-pad. L'interface comprend des boutons pour démarrer, réinitialiser et terminer la partie. Aussi, il affiche l'état du jeu, le score, et un paramètre de difficulté. Un bouton physique permet d'afficher un dessin enregistré, puis un autre enregistre un dessin à la fois. Ce jeu est inspiré du "memory leap frog de Lego Party". 

# Matériel utilise :
Le projet inclut un buzzer pour signaler un échec ou une tentative réussie, une LED RGB pour indiquer l'état (échec(rouge), réussite(vert), en jeux(bleue), connexion(jaune), connecte(blanc)), un joystick pour déplacer un point, un bouton poussoir pour basculer entre les modes sauvegarder/afficher des dessins, ainsi qu'une matrice LED 8x8 pour le jeu principal.

# À faire :
Configurer le Wi-Fi, développer un interface utilisateur, mettre en place un service de communication et automatiser le lancement des scripts (Wi-Fi, backend, frontend).

# Solution :
Pour ce faire, le wifi sera configurer sur le serveur 'rasp08' à l'aide de 'NetwerkManager' et 'dnsmasq.d'. Ensuite, l'interface sera un développer avec les langages de programmation suivante : HTML, CSS et Javascript.
Puis, le service de communication utiliser sera HTTP REST, parce qu'il facilitera l'échange de donnée entre les différents components. Finalement, le lancement des scripts sera effectué en tant que service 'systemd' de type 'oneshot'.
