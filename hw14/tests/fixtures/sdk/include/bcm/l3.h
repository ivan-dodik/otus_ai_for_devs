/**
 * @brief Add L3 route entry
 * @param unit Device unit number
 * @param route Route structure
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_l3_route_add(int unit, bcm_l3_route_t *route);
int bcm_l3_route_get(int unit, bcm_l3_route_t *route);
int bcm_l3_route_delete(int unit, bcm_l3_route_t *route);