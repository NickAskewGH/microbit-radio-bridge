/*
 * nRF52840 receive boundary for micro:bit MakeCode radio.
 *
 * This is intentionally a scaffold until the exact GeeekPi board SDK and
 * bootloader configuration are pinned. The implementation contract is:
 *
 *   RADIO: proprietary mode, 1 Mbit/s, whitening enabled, CRC enabled
 *   USB:   CDC ACM, one raw packet per lowercase hex line
 *
 * The micro:bit radio address and channel must be copied from the existing
 * mini-car-remote project during hardware bring-up. Do not transmit here.
 */

#include <stdint.h>

#define MAKECODE_GROUP 20u
#define MAX_RADIO_PAYLOAD 32u

static void radio_configure_rx(void) {
    /* TODO: configure NRF_RADIO->MODE, PREFIX0, BASE0, PCNF0/1, CRCCNF,
     * DATAWHITEIV, FREQUENCY and RXADDRESSES using the pinned SDK. */
}

static void usb_write_hex_line(const uint8_t *payload, uint8_t length) {
    /* TODO: write exactly 2*length ASCII hex characters followed by '\n'. */
    (void)payload;
    (void)length;
}

int main(void) {
    radio_configure_rx();

    for (;;) {
        /* TODO: arm a RADIO receive buffer, wait for END, then forward the
         * raw packet through USB. Keep this loop receive-only for milestone 1. */
        usb_write_hex_line((const uint8_t *)0, 0);
    }
}
