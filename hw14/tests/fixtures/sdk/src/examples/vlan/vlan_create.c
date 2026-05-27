/*
 * VLAN Create Example
 * Tested on: Trident3 (BCM56870)
 * Ports: 0-15
 * Tests: VLAN create/destroy
 */

#include <bcm/vlan.h>

int test_vlan_create(int unit) {
    int rv = bcm_vlan_create(unit, 100);
    return rv;
}