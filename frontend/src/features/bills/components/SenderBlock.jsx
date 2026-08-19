/**
 * Sender block — form fields for the sender party.
 */
import { PartyBlock } from './PartyBlock';

export function SenderBlock(props) {
  return <PartyBlock {...props} prefix="sender" />;
}

export default SenderBlock;
