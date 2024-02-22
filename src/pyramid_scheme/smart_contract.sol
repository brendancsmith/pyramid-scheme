// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract PyramidScheme is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable token;
    mapping(address => uint256) public earnings;
    mapping(address => address) public referrals;

    event JoinedScheme(address indexed participant, uint256 amount);
    event WithdrawnEarnings(address indexed participant, uint256 amount);
    event ReferredFriend(address indexed inviter, address indexed invitee);

    constructor(IERC20 _token) {
        require(address(_token) != address(0), "Token address cannot be zero.");
        token = _token;
    }

    function joinScheme(address _inviter, uint256 _amount) external nonReentrant {
        require(_amount > 0, "Amount must be greater than 0.");
        require(token.balanceOf(msg.sender) >= _amount, "Insufficient token balance.");
        
        // Transfer tokens to the contract
        token.safeTransferFrom(msg.sender, address(this), _amount);

        // Update earnings for the inviter if applicable
        if (_inviter != address(0) && _inviter != msg.sender) {
            uint256 referralBonus = _amount / 10; // 10% referral bonus
            earnings[_inviter] += referralBonus;
            referrals[msg.sender] = _inviter;
            emit ReferredFriend(_inviter, msg.sender);
        }

        // Emit event
        emit JoinedScheme(msg.sender, _amount);
    }

    function withdrawEarnings() external nonReentrant {
        uint256 amount = earnings[msg.sender];
        require(amount > 0, "No earnings to withdraw.");

        // Reset earnings before transferring to prevent re-entrancy attacks
        earnings[msg.sender] = 0;

        // Transfer earnings to the participant
        token.safeTransfer(msg.sender, amount);

        // Emit event
        emit WithdrawnEarnings(msg.sender, amount);
    }

    function viewEarnings(address _participant) external view returns (uint256) {
        return earnings[_participant];
    }

    function referFriend(address _invitee) external {
        require(_invitee != address(0), "Invitee address cannot be zero.");
        require(_invitee != msg.sender, "You cannot refer yourself.");
        require(referrals[_invitee] == address(0), "Invitee already referred.");

        referrals[_invitee] = msg.sender;
        emit ReferredFriend(msg.sender, _invitee);
    }
}
