/*
 * L3 Route Basic Example
 * Tested on: Tomahawk4 (BCM56980)
 * Ports: 0-31
 * Tests: IPv4 unicast route add/get/delete
 */

#include <bcm/l3.h>

int test_route_add(int unit) {
    bcm_l3_route_t route;
    bcm_l3_route_t_init(&route);
    BCM_IF_ERROR_RETURN(bcm_l3_route_add(unit, &route));
    return 0;
}