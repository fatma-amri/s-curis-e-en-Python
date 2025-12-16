#!/usr/bin/env python3
"""
Network diagnostic script to test P2P connection capabilities.
This script helps identify network configuration issues before running the main application.
"""

import socket
import sys
import platform


def diagnose_network():
    """Run comprehensive network diagnostics."""
    print("=" * 60)
    print("           DIAGNOSTIC RÉSEAU P2P")
    print("=" * 60)
    print()
    
    # 1. Vérifier l'adresse IP locale
    print("1. ADRESSE IP LOCALE")
    print("-" * 60)
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"✓ Hostname: {hostname}")
        print(f"✓ IP locale: {local_ip}")
        
        # Get better IP using UDP trick
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            better_ip = s.getsockname()[0]
            print(f"✓ IP réseau: {better_ip}")
        except Exception:
            better_ip = local_ip
        finally:
            s.close()
            
    except Exception as e:
        print(f"✗ Erreur IP locale: {e}")
    
    print()
    
    # 2. Tester la capacité d'écoute sur le port 5555
    print("2. TEST PORT 5555 (ÉCOUTE)")
    print("-" * 60)
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', 5555))
        test_socket.listen(1)
        print(f"✓ Port 5555 disponible pour écoute")
        print(f"✓ Socket bind sur 0.0.0.0:5555 réussi")
        test_socket.close()
    except OSError as e:
        if e.errno == 48 or e.errno == 98:
            print(f"✗ Port 5555 occupé: {e}")
            print(f"  Solution: Arrêter l'application utilisant le port ou choisir un autre port")
        else:
            print(f"✗ Port 5555 inaccessible: {e}")
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
    
    print()
    
    # 3. Tester les différents ports
    print("3. SCAN DES PORTS DISPONIBLES")
    print("-" * 60)
    available_ports = []
    for port in [5555, 5556, 5557, 5558, 5559]:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.bind(('0.0.0.0', port))
            test_socket.close()
            available_ports.append(port)
            print(f"✓ Port {port} disponible")
        except OSError:
            print(f"✗ Port {port} occupé")
    
    if available_ports:
        print(f"\nPorts disponibles: {', '.join(map(str, available_ports))}")
    else:
        print("\n⚠ Aucun port disponible dans la plage 5555-5559")
    
    print()
    
    # 4. Informations système
    print("4. INFORMATIONS SYSTÈME")
    print("-" * 60)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {sys.version.split()[0]}")
    
    print()
    
    # 5. Instructions firewall
    print("5. CONFIGURATION FIREWALL REQUISE")
    print("-" * 60)
    
    system = platform.system()
    
    if system == "Windows":
        print("WINDOWS - Ouvrir PowerShell en administrateur et exécuter:")
        print("  netsh advfirewall firewall add rule name='Python P2P' dir=in action=allow protocol=TCP localport=5555")
        print()
        print("Ou via l'interface graphique:")
        print("  1. Panneau de configuration → Pare-feu Windows Defender")
        print("  2. Paramètres avancés → Règles de trafic entrant")
        print("  3. Nouvelle règle → Port TCP 5555 → Autoriser")
        
    elif system == "Linux":
        print("LINUX - Exécuter ces commandes:")
        print("  sudo ufw allow 5555/tcp")
        print("  sudo ufw reload")
        print()
        print("Ou pour iptables:")
        print("  sudo iptables -A INPUT -p tcp --dport 5555 -j ACCEPT")
        print("  sudo iptables-save")
        
    elif system == "Darwin":  # macOS
        print("macOS - Configuration du pare-feu:")
        print("  1. Préférences Système → Sécurité et confidentialité")
        print("  2. Pare-feu → Options du pare-feu")
        print("  3. Ajouter Python à la liste des applications autorisées")
        print()
        print("Ou via Terminal:")
        print("  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3")
        print("  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3")
    
    print()
    
    # 6. Recommandations
    print("6. RECOMMANDATIONS")
    print("-" * 60)
    print("✓ Configurer le firewall pour autoriser le port 5555")
    print("✓ S'assurer que les deux machines sont sur le même réseau")
    print("✓ Vérifier qu'aucun VPN n'interfère avec les connexions locales")
    print("✓ Désactiver temporairement l'antivirus pour tester")
    print("✓ Utiliser l'IP réseau (pas 127.0.0.1) pour les connexions entre machines")
    
    print()
    print("=" * 60)
    print("         DIAGNOSTIC TERMINÉ")
    print("=" * 60)
    print()
    print("⚠ Si le port 5555 est occupé, utilisez un port différent dans l'application")
    print("⚠ Redémarrer l'application après configuration du firewall")


if __name__ == "__main__":
    diagnose_network()
