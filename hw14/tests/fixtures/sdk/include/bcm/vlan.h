/**
 * @brief Create a new VLAN
 * @param unit Device unit number
 * @param vlan VLAN ID
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_vlan_create(int unit, bcm_vlan_t vlan);

/**
 * @brief Destroy a VLAN
 * @param unit Device unit number
 * @param vlan VLAN ID
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_vlan_destroy(int unit, bcm_vlan_t vlan);

/**
 * @brief Get VLAN information
 * @param unit Device unit number
 * @param vlan VLAN ID
 * @param result Result buffer
 * @return BCM_E_NONE on success, error code otherwise
 */
int bcm_vlan_get(int unit, bcm_vlan_t vlan, bcm_vlan_t *result);