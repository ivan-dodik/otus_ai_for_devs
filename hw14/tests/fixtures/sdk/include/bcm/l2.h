/**
 * @brief Add L2 address entry
 * @param unit Device unit number
 * @param addr L2 address structure
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_l2_addr_add(int unit, bcm_l2_addr_t *addr);
int bcm_l2_addr_delete(int unit, bcm_l2_addr_t *addr);
int bcm_l2_addr_get(int unit, bcm_l2_addr_t *addr);