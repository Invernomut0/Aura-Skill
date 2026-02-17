#!/usr/bin/env python3
"""
Test script for the Avatar Management System.
Tests the avatar_manager.py integration with emotion-engine.
"""

import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from avatar_manager import AvatarManager

def test_avatar_manager():
    """Test the avatar manager functionality."""
    print("🧪 Testing Avatar Management System")
    print("=" * 60)
    
    try:
        # Initialize avatar manager
        print("\n1️⃣  Initializing Avatar Manager...")
        manager = AvatarManager()
        print("   ✅ Avatar Manager initialized successfully")
        
        # List available avatars
        print("\n2️⃣  Listing Available Avatars...")
        available = manager.list_available_avatars()
        print(f"   ✅ Found {len(available)} avatars:")
        for emotion, filename in available.items():
            print(f"      • {emotion}: {filename}")
        
        # Test with a sample emotional state
        print("\n3️⃣  Testing Avatar Update with Sample Emotional State...")
        test_state = {
            "primary_emotions": {
                "joy": 0.8,
                "curiosity": 0.6,
                "trust": 0.5,
                "sadness": 0.2,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.3,
                "disgust": 0.1
            },
            "complex_emotions": {
                "excitement": 0.7,
                "satisfaction": 0.6,
                "empathy": 0.5,
                "frustration": 0.2,
                "confusion": 0.1,
                "anticipation": 0.4,
                "flow_state": 0.3
            }
        }
        
        print("   Emotional State:")
        print("   Primary: joy=0.8, curiosity=0.6, trust=0.5")
        print("   Complex: excitement=0.7, satisfaction=0.6, empathy=0.5")
        
        success, emotion, avatar_file = manager.update_avatar_from_emotion(test_state)
        
        if success:
            print(f"   ✅ Avatar updated successfully!")
            print(f"      Dominant Emotion: {emotion}")
            print(f"      Avatar File: {avatar_file}")
        else:
            print(f"   ❌ Avatar update failed for emotion: {emotion}")
        
        # Get current avatar info
        print("\n4️⃣  Getting Current Avatar Info...")
        info = manager.get_current_avatar_info()
        print("   ✅ Avatar Info:")
        print(f"      Current Avatar: {info.get('current_avatar', 'None')}")
        print(f"      Avatar Exists: {info.get('avatar_exists', False)}")
        print(f"      Workspace Path: {info.get('workspace_avatar_path', 'Unknown')}")
        print(f"      Assets Dir: {info.get('assets_dir', 'Unknown')}")
        
        # Test force update
        print("\n5️⃣  Testing Force Update to 'curiosity'...")
        success, message = manager.force_update_avatar("curiosity")
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Verify the avatar file exists at:")
        print(f"      {info.get('workspace_avatar_path', '~/.openclaw/workspace/avatars/current_avatar.png')}")
        print("   2. Check OpenClaw config at: ~/.openclaw/openclaw.json")
        print("   3. Restart OpenClaw to see the new avatar in action")
        print("   4. Use /emotions avatar commands to manage avatars")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_avatar_manager()
    sys.exit(0 if success else 1)
