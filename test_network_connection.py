#!/usr/bin/env python3
"""
Test script for network P2P connection between two machines.
Run in server mode on one machine and client mode on another.
"""

import socket
import sys
import time


def get_local_ip():
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address to get local IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def server_mode(port=5555):
    """Run in server mode (accept connections)."""
    local_ip = get_local_ip()
    print()
    print("=" * 60)
    print("           MODE SERVEUR")
    print("=" * 60)
    print(f"IP locale: {local_ip}")
    print(f"Port: {port}")
    print()
    print(f"⚠ Donnez cette adresse au client: {local_ip}:{port}")
    print("=" * 60)
    print()
    
    try:
        # Créer le socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind sur toutes les interfaces
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        
        print(f"[SERVEUR] Socket créé et lié à 0.0.0.0:{port}")
        print(f"[SERVEUR] En attente de connexion...")
        print(f"[SERVEUR] (Appuyez sur Ctrl+C pour arrêter)")
        print()
        
        # Accepter la connexion
        conn, addr = sock.accept()
        print(f"\n✓✓✓ CONNEXION ÉTABLIE ✓✓✓")
        print(f"Peer: {addr[0]}:{addr[1]}")
        print()
        
        # Test d'échange de messages
        print("Test d'échange de messages:")
        print("-" * 60)
        
        for i in range(5):
            try:
                # Recevoir un message
                data = conn.recv(1024)
                if not data:
                    print("[SERVEUR] Connexion fermée par le peer")
                    break
                    
                message = data.decode('utf-8')
                print(f"[REÇU] {message}")
                
                # Envoyer une réponse
                response = f"ACK: {message}"
                conn.sendall(response.encode('utf-8'))
                print(f"[ENVOYÉ] {response}")
                print()
                
            except Exception as e:
                print(f"[ERREUR] {e}")
                break
        
        print("-" * 60)
        print("✓ Test de connexion terminé avec succès")
        
    except KeyboardInterrupt:
        print("\n\n[SERVEUR] Arrêt demandé par l'utilisateur")
    except OSError as e:
        if e.errno == 48 or e.errno == 98:
            print(f"✗ ERREUR: Port {port} déjà utilisé")
            print(f"  Solution: Arrêter l'application utilisant le port ou choisir un autre port")
            print(f"  Exemple: python {sys.argv[0]} server {port + 1}")
        else:
            print(f"✗ ERREUR OS: {e}")
    except Exception as e:
        print(f"✗ ERREUR INATTENDUE: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
        if 'sock' in locals():
            sock.close()
        print("\n[SERVEUR] Socket fermé")


def client_mode(host, port=5555):
    """Run in client mode (connect to server)."""
    print()
    print("=" * 60)
    print("           MODE CLIENT")
    print("=" * 60)
    print(f"Connexion à {host}:{port}")
    print("=" * 60)
    print()
    
    try:
        # Valider l'adresse IP
        try:
            socket.inet_aton(host)
            print(f"[CLIENT] Adresse IP valide: {host}")
        except socket.error:
            print(f"✗ ERREUR: Adresse IP invalide: {host}")
            return
        
        # Créer le socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print(f"[CLIENT] Socket créé")
        print(f"[CLIENT] Tentative de connexion à {host}:{port}...")
        print(f"[CLIENT] (Timeout: 10 secondes)")
        print()
        
        # Se connecter
        sock.connect((host, port))
        print(f"✓✓✓ CONNECTÉ À {host}:{port} ✓✓✓")
        print()
        
        # Remettre le timeout à None pour les opérations normales
        sock.settimeout(None)
        
        # Test d'envoi de messages
        print("Test d'échange de messages:")
        print("-" * 60)
        
        for i in range(5):
            try:
                # Envoyer un message
                message = f"Test message {i + 1}"
                print(f"[ENVOYÉ] {message}")
                sock.sendall(message.encode('utf-8'))
                
                # Recevoir la réponse
                data = sock.recv(1024)
                response = data.decode('utf-8')
                print(f"[REÇU] {response}")
                print()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"[ERREUR] {e}")
                break
        
        print("-" * 60)
        print("✓ Test de connexion terminé avec succès")
        
    except socket.timeout:
        print(f"✗ TIMEOUT: Impossible de se connecter à {host}:{port} après 10 secondes")
        print()
        print("Causes possibles:")
        print("  1. Le serveur n'est pas démarré sur l'autre machine")
        print("  2. Le firewall bloque la connexion")
        print("  3. L'adresse IP est incorrecte")
        print("  4. Les machines ne sont pas sur le même réseau")
        print()
        print("Solutions:")
        print("  1. Vérifier que le serveur est bien démarré")
        print("  2. Configurer le firewall (exécuter 'python network_debug.py')")
        print("  3. Vérifier l'adresse IP avec 'ipconfig' (Windows) ou 'ifconfig' (Linux/Mac)")
        print("  4. Essayer de ping l'autre machine")
        
    except ConnectionRefusedError:
        print(f"✗ CONNEXION REFUSÉE: Le serveur {host}:{port} refuse la connexion")
        print()
        print("Causes possibles:")
        print("  1. Le serveur n'est pas démarré")
        print("  2. Le serveur écoute sur un autre port")
        print("  3. Le firewall bloque la connexion")
        print()
        print("Solutions:")
        print("  1. Démarrer le serveur en mode serveur d'abord")
        print("  2. Vérifier le numéro de port")
        print("  3. Configurer le firewall")
        
    except socket.gaierror as e:
        print(f"✗ ERREUR DNS/ADRESSE: {e}")
        print()
        print("Vérifiez que l'adresse IP est correcte")
        print("Exemple d'adresse valide: 192.168.1.10")
        
    except OSError as e:
        print(f"✗ ERREUR OS: {e}")
        
    except Exception as e:
        print(f"✗ ERREUR INATTENDUE: {type(e).__name__}: {e}")
        
    finally:
        if 'sock' in locals():
            sock.close()
        print("\n[CLIENT] Socket fermé")


def print_usage():
    """Print usage information."""
    print()
    print("=" * 60)
    print("      TEST CONNEXION RÉSEAU P2P")
    print("=" * 60)
    print()
    print("Usage:")
    print(f"  Mode serveur:  python {sys.argv[0]} server [port]")
    print(f"  Mode client:   python {sys.argv[0]} client <ip> [port]")
    print()
    print("Exemples:")
    print(f"  python {sys.argv[0]} server")
    print(f"  python {sys.argv[0]} server 5556")
    print(f"  python {sys.argv[0]} client 192.168.1.10")
    print(f"  python {sys.argv[0]} client 192.168.1.10 5556")
    print()
    print("Instructions:")
    print("  1. Sur la machine A, exécuter en mode serveur")
    print("  2. Noter l'adresse IP affichée")
    print("  3. Sur la machine B, exécuter en mode client avec l'IP de A")
    print("  4. Observer l'échange de messages")
    print()
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == "server":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
        server_mode(port)
        
    elif mode == "client":
        if len(sys.argv) < 3:
            print("✗ ERREUR: Adresse IP du serveur requise")
            print_usage()
            sys.exit(1)
        host = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 5555
        client_mode(host, port)
        
    else:
        print(f"✗ Mode invalide: {mode}")
        print_usage()
        sys.exit(1)
