RPC_MESSAGES_TO_RETRY = {
    'request failed or timed out',
}


def should_retry_rpc_error(error_msg):
    try:
        return error_msg.lower().strip() in RPC_MESSAGES_TO_RETRY
    except Exception:
        return False


class BlockchainRPCError(Exception):
    pass


class BlockchainAddressValidationError(Exception):
    pass
