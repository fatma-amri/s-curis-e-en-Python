#!/usr/bin/env python3
"""
Test script for localhost P2P connection.
Tests basic socket connectivity on the local machine.
"""

import socket
import threading
import time
import sys


def test_localhost():
    """Test localhost connection between server and client."""
    print("=" * 60)
    print("      TEST CONNEXION LOCALHOST")
    print("=" * 60)
    print()
    
    PORT = 5555
    success = False
    server_error = None
    client_error = None
    
    # Thread serveur
    def server():
        nonlocal server_error
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try different binding strategies
            try:
                sock.bind(('127.0.0.1', PORT))
                print(f"[SERVEUR] Bind sur 127.0.0.1:{PORT}")
            except OSError as e:
                if e.errno in (98, 99):  # EADDRINUSE or EADDRNOTAVAIL
                    # Bind to 0.0.0.0 is intentional: fallback to accept from any interface
                    sock.bind(('0.0.0.0', PORT))
                    print(f"[SERVEUR] Bind sur 0.0.0.0:{PORT}")
                else:
                    raise
            
            sock.listen(1)
            sock.settimeout(10)  # 10 seconds timeout
            print("[SERVEUR] En écoute...")
            
            conn, addr = sock.accept()
            print(f"[SERVEUR] ✓ Connexion acceptée de {addr[0]}:{addr[1]}")
            
            # Recevoir un message
            data = conn.recv(1024)
            message = data.decode('utf-8')
            print(f"[SERVEUR] Message reçu: {message}")
            
            # Envoyer une réponse
            conn.sendall(b"Pong")
            print("[SERVEUR] Réponse 'Pong' envoyée")
            
            time.sleep(0.2)
            conn.close()
            sock.close()
            print("[SERVEUR] Socket fermé proprement")
            
        except socket.timeout:
            server_error = "Timeout - Aucune connexion reçue après 10 secondes"
            print(f"[SERVEUR] ✗ {server_error}")
        except Exception as e:
            server_error = str(e)
            print(f"[SERVEUR] ✗ Erreur: {e}")
    
    # Démarrer le serveur dans un thread
    server_thread = threading.Thread(target=server, daemon=True)
    server_thread.start()
    
    # Attendre que le serveur démarre
    time.sleep(0.5)
    
    # Thread client
    print("\n[CLIENT] Démarrage du client...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print(f"[CLIENT] Connexion à 127.0.0.1:{PORT}...")
        
        sock.connect(('127.0.0.1', PORT))
        print("[CLIENT] ✓ Connecté au serveur")
        
        # Envoyer un message
        sock.sendall(b"Ping")
        print("[CLIENT] Message 'Ping' envoyé")
        
        # Recevoir la réponse
        data = sock.recv(1024)
        response = data.decode('utf-8')
        print(f"[CLIENT] Réponse reçue: {response}")
        
        if response == "Pong":
            print("[CLIENT] ✓ Réponse correcte")
            success = True
        else:
            print(f"[CLIENT] ✗ Réponse incorrecte: attendu 'Pong', reçu '{response}'")
        
        sock.close()
        print("[CLIENT] Socket fermé proprement")
        
    except socket.timeout:
        client_error = "Timeout - Le serveur ne répond pas"
        print(f"[CLIENT] ✗ {client_error}")
    except ConnectionRefusedError:
        client_error = "Connexion refusée - Le serveur n'accepte pas la connexion"
        print(f"[CLIENT] ✗ {client_error}")
    except Exception as e:
        client_error = str(e)
        print(f"[CLIENT] ✗ Erreur: {e}")
    
    # Attendre que le thread serveur se termine
    server_thread.join(timeout=2)
    
    # Résultat du test
    print()
    print("=" * 60)
    if success and not server_error and not client_error:
        print("✓✓✓ TEST RÉUSSI - Connexion localhost fonctionne ✓✓✓")
        print()
        print("La connexion P2P de base fonctionne correctement.")
        print("Vous pouvez maintenant tester une connexion réseau.")
        return_code = 0
    else:
        print("✗✗✗ TEST ÉCHOUÉ - Problème de connexion ✗✗✗")
        print()
        if server_error:
            print(f"Erreur serveur: {server_error}")
        if client_error:
            print(f"Erreur client: {client_error}")
        print()
        print("Suggestions:")
        print("  1. Vérifier qu'aucune autre application n'utilise le port 5555")
        print("  2. Exécuter 'python network_debug.py' pour plus d'informations")
        print("  3. Vérifier les permissions du firewall")
        return_code = 1
    
    print("=" * 60)
    return return_code


if __name__ == "__main__":
    exit_code = test_localhost()
    sys.exit(exit_code)
