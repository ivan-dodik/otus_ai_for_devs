#include <bcm/l2.h>

int bcm_esw_l2_addr_add(int unit, bcm_l2_addr_t *addr) {
    return _bcm_esw_l2_addr_add_internal(unit, addr);
}

static int _bcm_esw_l2_addr_add_internal(int unit, bcm_l2_addr_t *addr) {
    if (SOC_IS_TOMAHAWK4(unit)) {
        return th4_l2_entry_insert(unit, addr);
    }
    return BCM_E_UNAVAIL;
}

#if defined(BCM_TOMAHAWK4_SUPPORT)
static int th4_l2_entry_insert(int unit, bcm_l2_addr_t *addr) {
    /* Tomahawk4 specific implementation */
    return BCM_E_NONE;
}
#endif