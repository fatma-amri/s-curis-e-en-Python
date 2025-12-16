# Guide de Dépannage Réseau P2P

Ce guide vous aide à diagnostiquer et résoudre les problèmes de connexion réseau dans l'application P2P.

## 🔍 Outils de Diagnostic

### 1. Script de Diagnostic Réseau

Avant de démarrer l'application, exécutez le script de diagnostic :

```bash
python network_debug.py
```

Ce script vérifie :
- ✓ Adresse IP locale et réseau
- ✓ Disponibilité du port 5555
- ✓ Scan des ports disponibles
- ✓ Configuration système
- ✓ Instructions firewall

### 2. Test de Connexion Localhost

Pour vérifier que les connexions de base fonctionnent :

```bash
python test_localhost_connection.py
```

✓ **TEST RÉUSSI** = Les sockets fonctionnent correctement  
✗ **TEST ÉCHOUÉ** = Problème de configuration système

### 3. Test de Connexion Réseau

Pour tester la connexion entre deux machines :

**Sur la machine A (serveur):**
```bash
python test_network_connection.py server
```

**Sur la machine B (client):**
```bash
python test_network_connection.py client <IP_de_A>
```

## 🐛 Problèmes Courants et Solutions

### Problème 1: Port Déjà Utilisé

**Symptômes:**
```
OSError: [Errno 48] Address already in use  (macOS)
OSError: [Errno 98] Address already in use  (Linux)
```

**Solutions:**

1. **Trouver et arrêter le processus utilisant le port:**
   ```bash
   # Linux/macOS
   lsof -i :5555
   kill -9 <PID>
   
   # Windows
   netstat -ano | findstr :5555
   taskkill /PID <PID> /F
   ```

2. **Utiliser un port différent:**
   - Dans l'application, choisissez un port différent (ex: 5556, 5557)
   - Le script `network_debug.py` vous montre les ports disponibles

3. **L'option SO_REUSEADDR est maintenant activée automatiquement** dans le code

### Problème 2: Connexion Refusée

**Symptômes:**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Causes Possibles:**
1. Le serveur n'est pas démarré
2. Mauvaise adresse IP ou port
3. Firewall bloque la connexion
4. Le serveur écoute sur la mauvaise interface

**Solutions:**

1. **Vérifier que le serveur est démarré:**
   - Sur la machine serveur, démarrez l'application en mode "Listen (Server Mode)"
   - Attendez le message "Waiting for incoming connection..."

2. **Vérifier l'adresse IP:**
   ```bash
   # Linux/macOS
   ifconfig
   ip addr show
   
   # Windows
   ipconfig
   ```
   
   Utilisez l'adresse IP du réseau local (ex: 192.168.x.x), PAS 127.0.0.1

3. **Tester la connectivité réseau:**
   ```bash
   ping <IP_du_serveur>
   ```

4. **Configurer le firewall** (voir section Firewall ci-dessous)

### Problème 3: Timeout de Connexion

**Symptômes:**
```
socket.timeout: timed out
```

**Solutions:**

1. **Vérifier que les machines sont sur le même réseau**
2. **Désactiver le VPN temporairement**
3. **Augmenter le timeout** (déjà configuré à 10 secondes)
4. **Vérifier la configuration firewall**

### Problème 4: Handshake Échoue

**Symptômes:**
- Connexion établie mais le handshake ne se termine pas
- Messages d'erreur dans les logs

**Solutions:**

1. **Vérifier les logs détaillés:**
   ```bash
   cat data/logs/network_manager.log
   ```

2. **Régénérer les clés:**
   - Supprimer le répertoire `data/keys/`
   - Redémarrer l'application
   - Créer un nouveau mot de passe

3. **Vérifier la version:**
   - Assurez-vous que les deux machines utilisent la même version de l'application

### Problème 5: Interface Bloquée

**Symptômes:**
- L'interface ne répond plus pendant la connexion
- L'application freeze

**Solutions:**

✓ **Déjà corrigé** : Les opérations réseau sont maintenant dans des threads séparés

Si le problème persiste :
1. Redémarrer l'application
2. Vérifier les logs pour des erreurs
3. Utiliser un timeout plus court

## 🛡️ Configuration Firewall

### Windows

**Méthode 1: PowerShell (Recommandé)**
```powershell
# Exécuter en administrateur
netsh advfirewall firewall add rule name="Python P2P" dir=in action=allow protocol=TCP localport=5555
```

**Méthode 2: Interface Graphique**
1. Panneau de configuration → Pare-feu Windows Defender
2. Paramètres avancés → Règles de trafic entrant
3. Nouvelle règle
4. Type de règle : Port
5. Protocole et ports : TCP, port local 5555
6. Action : Autoriser la connexion
7. Profil : Cocher les trois (Domaine, Privé, Public)
8. Nom : Python P2P Messenger

### Linux (Ubuntu/Debian)

**Avec UFW (Recommandé):**
```bash
sudo ufw allow 5555/tcp
sudo ufw reload
sudo ufw status
```

**Avec iptables:**
```bash
sudo iptables -A INPUT -p tcp --dport 5555 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

### macOS

**Méthode 1: Interface Graphique**
1. Préférences Système → Sécurité et confidentialité
2. Pare-feu → Options du pare-feu
3. Cliquer sur le cadenas pour déverrouiller
4. Cliquer sur "+" pour ajouter une application
5. Sélectionner Python
6. Autoriser les connexions entrantes

**Méthode 2: Terminal**
```bash
# Ajouter Python à la liste des applications autorisées
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3
```

## 📊 Logs et Débogage

### Activer les Logs Détaillés

Les logs DEBUG sont maintenant activés par défaut. Consultez-les :

```bash
# Logs en temps réel
tail -f data/logs/network_manager.log

# Rechercher des erreurs
grep ERROR data/logs/network_manager.log
grep "handshake" data/logs/network_manager.log
```

### Comprendre les Messages de Log

**Connexion réussie:**
```
INFO - ✓ CONNECTED to 192.168.1.10:5555
INFO - ✓✓✓ HANDSHAKE COMPLETE (client) ✓✓✓
```

**Erreur de connexion:**
```
ERROR - CONNECTION REFUSED: Server at 192.168.1.10:5555 refused the connection
INFO - Check that:
INFO -   1. Server is started in server mode
INFO -   2. Port number is correct
INFO -   3. Firewall allows connections
```

**Problème de handshake:**
```
ERROR - Invalid signature in HELLO message
WARNING - SECURITY: Signature verification failed - possible MITM attack
```

## 🔧 Commandes Utiles

### Vérifier les Connexions Actives

**Linux/macOS:**
```bash
# Voir toutes les connexions
netstat -an | grep 5555

# Voir les processus utilisant le port
lsof -i :5555

# Vérifier les connexions établies
ss -t | grep 5555
```

**Windows:**
```cmd
# Voir toutes les connexions
netstat -an | findstr 5555

# Voir les processus
netstat -ano | findstr 5555
```

### Tester la Connectivité

```bash
# Ping l'autre machine
ping <IP_peer>

# Tester si le port est ouvert (Linux/macOS)
nc -zv <IP_peer> 5555
telnet <IP_peer> 5555

# Tester si le port est ouvert (Windows)
Test-NetConnection -ComputerName <IP_peer> -Port 5555
```

## ✅ Checklist de Dépannage

Avant de contacter le support, vérifiez :

### Vérifications de Base
- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] `python network_debug.py` réussit
- [ ] `python test_localhost_connection.py` réussit
- [ ] Port 5555 disponible
- [ ] Adresse IP correcte obtenue

### Vérifications Réseau
- [ ] Les deux machines sont sur le même réseau
- [ ] Ping fonctionne entre les machines
- [ ] Firewall configuré pour autoriser le port 5555
- [ ] Pas de VPN actif
- [ ] Antivirus ne bloque pas Python

### Vérifications Application
- [ ] Même version sur les deux machines
- [ ] Clés cryptographiques générées
- [ ] Mot de passe créé/connu
- [ ] Un peer en mode serveur, l'autre en mode client
- [ ] IP et port corrects entrés

### Tests Effectués
- [ ] Test localhost réussit
- [ ] Test avec IP locale réussit
- [ ] Test entre deux machines réussit
- [ ] Handshake se termine sans erreur
- [ ] Messages s'échangent correctement

## 🆘 Support

Si les problèmes persistent après avoir suivi ce guide :

1. **Collecter les informations:**
   ```bash
   python network_debug.py > diagnostic.txt
   tail -100 data/logs/network_manager.log > logs.txt
   ```

2. **Créer une issue sur GitHub** avec :
   - Description du problème
   - Fichiers diagnostic.txt et logs.txt
   - Système d'exploitation et version Python
   - Étapes pour reproduire le problème

## 📚 Références

- [Documentation Socket Python](https://docs.python.org/3/library/socket.html)
- [Guide Firewall Windows](https://support.microsoft.com/en-us/windows/turn-microsoft-defender-firewall-on-or-off-ec0844f7-aebd-0583-67fe-601ecf5d774f)
- [Guide UFW Ubuntu](https://help.ubuntu.com/community/UFW)
- [Networking Basics](https://www.cloudflare.com/learning/network-layer/what-is-a-computer-network/)

---

💡 **Astuce:** Gardez les logs de diagnostic et les scripts de test à portée de main lors du déploiement sur de nouvelles machines.
