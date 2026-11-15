#!/bin/bash
set -e

# SSH Key Setup Script
# Usage: bash scripts/setup-ssh-keys.sh
# Generates SSH keys and configures them for remote access

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

SSH_DIR="$HOME/.ssh"
SSH_KEY="$SSH_DIR/id_rsa_request_system"
SSH_PUB_KEY="$SSH_KEY.pub"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           SSH Key Setup Script                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Create .ssh directory if it doesn't exist
if [ ! -d "$SSH_DIR" ]; then
    log_info "Creating .ssh directory..."
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    log_success ".ssh directory created"
fi

# Check if key already exists
if [ -f "$SSH_KEY" ]; then
    log_warning "SSH key already exists: $SSH_KEY"
    read -p "Do you want to regenerate it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Using existing key"
        echo ""
        log_info "Public key:"
        cat "$SSH_PUB_KEY"
        echo ""
        log_info "To add this key to your VPS, copy the line above and run on the server:"
        echo "  echo '$(cat $SSH_PUB_KEY)' >> ~/.ssh/authorized_keys"
        exit 0
    fi
fi

# Generate new SSH key
log_info "Generating new SSH key..."
log_info "Key path: $SSH_KEY"
log_info "Key type: RSA 4096-bit"
log_info ""
log_info "Enter a passphrase (leave empty for no passphrase):"

ssh-keygen -t rsa -b 4096 -f "$SSH_KEY" -C "request-system-deploy" -N ""

if [ $? -eq 0 ]; then
    log_success "SSH key generated successfully"
    chmod 600 "$SSH_KEY"
    chmod 644 "$SSH_PUB_KEY"
else
    log_error "Failed to generate SSH key"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Key Information                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
log_info "Private key:  $SSH_KEY"
log_info "Public key:   $SSH_PUB_KEY"
echo ""
log_warning "KEEP YOUR PRIVATE KEY SECURE!"
echo ""

# Display public key
echo "Your public key:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$SSH_PUB_KEY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Instructions
echo "Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Copy the public key above"
echo ""
echo "2. SSH to your VPS server:"
echo "   ssh ubuntu@your-vps-ip"
echo ""
echo "3. Add the public key to authorized_keys:"
echo "   mkdir -p ~/.ssh"
echo "   echo 'PASTE_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys"
echo "   chmod 700 ~/.ssh"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "4. Test the connection from your local machine:"
echo "   ssh -i $SSH_KEY ubuntu@your-vps-ip"
echo ""
echo "5. Update your deployment script to use the key:"
echo "   ssh -i $SSH_KEY ubuntu@your-vps-ip"
echo ""

# Optional: Add to SSH config
read -p "Would you like to add this key to your SSH config? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your VPS hostname/IP: " VPS_HOST
    read -p "Enter your VPS username (default: ubuntu): " VPS_USER
    VPS_USER=${VPS_USER:-ubuntu}
    
    SSH_CONFIG="$SSH_DIR/config"
    
    if [ ! -f "$SSH_CONFIG" ]; then
        touch "$SSH_CONFIG"
        chmod 600 "$SSH_CONFIG"
    fi
    
    # Add config entry
    cat >> "$SSH_CONFIG" << EOFCONFIG
Host request-system-vps
    HostName $VPS_HOST
    User $VPS_USER
    IdentityFile $SSH_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOFCONFIG
    
    log_success "SSH config updated!"
    echo "You can now connect with: ssh request-system-vps"
fi

echo ""
log_success "SSH key setup completed!"
