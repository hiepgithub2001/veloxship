/**
 * Receiver block — form fields for the receiver party.
 */
import { PartyBlock } from './PartyBlock';

export function ReceiverBlock(props) {
  return <PartyBlock {...props} prefix="receiver" />;
}

export default ReceiverBlock;
