// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title ProofOfSkillSwarm
 * @dev ERC-1155 based skill verification and NFT minting system with ERC-6551 tokenbound account support
 */
contract ProofOfSkillSwarm is ERC1155, Ownable, ReentrancyGuard {
    struct SkillChallenge {
        uint256 challengeId;
        string challengeType;
        uint256 difficulty;
        uint256 timeLimit;
        uint256 reward;
        bool isActive;
        address creator;
        bytes32 challengeHash;
    }
    
    struct SkillProof {
        uint256 proofId;
        uint256 challengeId;
        address solver;
        uint256 completionTime;
        uint256 score;
        bytes32 solutionHash;
        bytes32 zkProof;
        bool verified;
    }
    
    struct SkillNFT {
        uint256 tokenId;
        address owner;
        string skillType;
        uint256 proficiencyLevel;
        uint256 totalEarnings;
        uint256 verificationCount;
        uint256 createdAt;
    }
    
    // State variables
    mapping(uint256 => SkillChallenge) public challenges;
    mapping(uint256 => SkillProof) public proofs;
    mapping(uint256 => SkillNFT) public skillNFTs;
    mapping(uint256 => bytes32[]) public nftProofHashes;
    mapping(address => uint256[]) public userChallenges;
    mapping(address => uint256[]) public userProofs;
    mapping(address => uint256[]) public userNFTs;
    
    address public immutable registry;
    uint256 public challengeCounter;
    uint256 public proofCounter;
    uint256 public nftCounter;
    
    // Events
    event ChallengeCreated(uint256 indexed challengeId, string challengeType, uint256 difficulty, address creator);
    event ChallengeCompleted(uint256 indexed challengeId, address indexed solver, uint256 score);
    event SkillNFTMinted(uint256 indexed tokenId, address indexed owner, string skillType, uint256 proficiencyLevel);
    event SkillNFTUpdated(uint256 indexed tokenId, uint256 newProficiencyLevel, uint256 verificationCount);
    event SkillVerified(uint256 indexed proofId, bool verified);
    event TokenBoundAccountCreated(uint256 indexed tokenId, address account);
    
    constructor(address _registry) ERC1155("https://api.proofofskill.swarm/metadata/{id}") {
        registry = _registry;
    }
    
    /**
     * @dev Create a new skill challenge
     */
    function createChallenge(
        string memory _challengeType,
        uint256 _difficulty,
        uint256 _timeLimit,
        uint256 _reward,
        bytes32 _challengeHash
    ) external payable returns (uint256) {
        require(_difficulty > 0 && _difficulty <= 10, "Invalid difficulty");
        require(_timeLimit > 0, "Invalid time limit");
        require(msg.value >= _reward, "Insufficient reward funding");
        
        challengeCounter++;
        challenges[challengeCounter] = SkillChallenge({
            challengeId: challengeCounter,
            challengeType: _challengeType,
            difficulty: _difficulty,
            timeLimit: _timeLimit,
            reward: _reward,
            isActive: true,
            creator: msg.sender,
            challengeHash: _challengeHash
        });
        
        userChallenges[msg.sender].push(challengeCounter);
        emit ChallengeCreated(challengeCounter, _challengeType, _difficulty, msg.sender);
        return challengeCounter;
    }
    
    /**
     * @dev Submit a proof for a challenge
     */
    function submitProof(
        uint256 _challengeId,
        uint256 _completionTime,
        uint256 _score,
        bytes32 _solutionHash,
        bytes32 _zkProof
    ) external nonReentrant returns (uint256) {
        require(challenges[_challengeId].isActive, "Challenge not active");
        require(_completionTime <= challenges[_challengeId].timeLimit, "Time limit exceeded");
        require(_score <= 100, "Invalid score");
        
        proofCounter++;
        proofs[proofCounter] = SkillProof({
            proofId: proofCounter,
            challengeId: _challengeId,
            solver: msg.sender,
            completionTime: _completionTime,
            score: _score,
            solutionHash: _solutionHash,
            zkProof: _zkProof,
            verified: false
        });
        
        userProofs[msg.sender].push(proofCounter);
        emit ChallengeCompleted(_challengeId, msg.sender, _score);
        
        return proofCounter;
    }
    
    /**
     * @dev Verify a submitted proof and mint/update NFT
     */
    function verifyProof(uint256 _proofId) external {
        require(proofs[_proofId].verified == false, "Proof already verified");
        
        // ZK-proof verification
        bool isValid = verifyZKProof(proofs[_proofId].zkProof);
        
        if (isValid) {
            proofs[_proofId].verified = true;
            
            // Check if user already has a skill NFT for this type
            uint256 existingNFT = findUserSkillNFT(
                proofs[_proofId].solver, 
                challenges[proofs[_proofId].challengeId].challengeType
            );
            
            if (existingNFT > 0) {
                // Update existing NFT
                uint256 newProficiency = calculateNewProficiency(existingNFT, proofs[_proofId].score);
                skillNFTs[existingNFT].proficiencyLevel = newProficiency;
                skillNFTs[existingNFT].verificationCount++;
                nftProofHashes[existingNFT].push(proofs[_proofId].solutionHash);
                
                emit SkillNFTUpdated(existingNFT, newProficiency, skillNFTs[existingNFT].verificationCount);
            } else {
                // Mint new skill NFT
                nftCounter++;
                uint256 proficiency = calculateInitialProficiency(proofs[_proofId].score);
                
                skillNFTs[nftCounter] = SkillNFT({
                    tokenId: nftCounter,
                    owner: proofs[_proofId].solver,
                    skillType: challenges[proofs[_proofId].challengeId].challengeType,
                    proficiencyLevel: proficiency,
                    totalEarnings: 0,
                    verificationCount: 1,
                    createdAt: block.timestamp
                });
                
                nftProofHashes[nftCounter].push(proofs[_proofId].solutionHash);
                userNFTs[proofs[_proofId].solver].push(nftCounter);
                
                _mint(proofs[_proofId].solver, nftCounter, 1, "");
                emit SkillNFTMinted(
                    nftCounter, 
                    proofs[_proofId].solver, 
                    challenges[proofs[_proofId].challengeId].challengeType,
                    proficiency
                );
            }
            
            // Transfer reward
            if (challenges[proofs[_proofId].challengeId].reward > 0) {
                payable(proofs[_proofId].solver).transfer(challenges[proofs[_proofId].challengeId].reward);
            }
        }
        
        emit SkillVerified(_proofId, isValid);
    }
    
    /**
     * @dev Create tokenbound account for NFT (ERC-6551 compatibility)
     */
    function createTokenBoundAccount(uint256 _tokenId) external returns (address) {
        require(balanceOf(msg.sender, _tokenId) > 0, "Not token owner");
        require(registry != address(0), "Registry not set");
        
        // In production, this would call the ERC-6551 registry
        // For now, we emit an event
        address account = address(uint160(uint256(keccak256(abi.encodePacked(_tokenId, block.timestamp)))));
        
        emit TokenBoundAccountCreated(_tokenId, account);
        return account;
    }
    
    /**
     * @dev Deactivate a challenge
     */
    function deactivateChallenge(uint256 _challengeId) external {
        require(challenges[_challengeId].creator == msg.sender, "Not challenge creator");
        challenges[_challengeId].isActive = false;
    }
    
    /**
     * @dev Get user's skill NFTs
     */
    function getUserNFTs(address _user) external view returns (uint256[] memory) {
        return userNFTs[_user];
    }
    
    /**
     * @dev Get NFT proof hashes
     */
    function getNFTProofHashes(uint256 _tokenId) external view returns (bytes32[] memory) {
        return nftProofHashes[_tokenId];
    }
    
    /**
     * @dev Get user's proofs
     */
    function getUserProofs(address _user) external view returns (uint256[] memory) {
        return userProofs[_user];
    }
    
    /**
     * @dev Get user's challenges
     */
    function getUserChallenges(address _user) external view returns (uint256[] memory) {
        return userChallenges[_user];
    }
    
    // Internal functions
    
    function verifyZKProof(bytes32 _zkProof) internal pure returns (bool) {
        // Simplified ZK-proof verification
        // In production, this would interface with a ZK-proof verification library
        return _zkProof != bytes32(0);
    }
    
    function findUserSkillNFT(address _user, string memory _skillType) internal view returns (uint256) {
        uint256[] memory nfts = userNFTs[_user];
        for (uint256 i = 0; i < nfts.length; i++) {
            if (keccak256(bytes(skillNFTs[nfts[i]].skillType)) == keccak256(bytes(_skillType))) {
                return nfts[i];
            }
        }
        return 0;
    }
    
    function calculateInitialProficiency(uint256 _score) internal pure returns (uint256) {
        // Convert score (0-100) to proficiency level (1-10)
        if (_score >= 90) return 10;
        if (_score >= 80) return 9;
        if (_score >= 70) return 8;
        if (_score >= 60) return 7;
        if (_score >= 50) return 6;
        if (_score >= 40) return 5;
        if (_score >= 30) return 4;
        if (_score >= 20) return 3;
        if (_score >= 10) return 2;
        return 1;
    }
    
    function calculateNewProficiency(uint256 _tokenId, uint256 _score) internal view returns (uint256) {
        // Weighted average of current proficiency and new score
        uint256 currentLevel = skillNFTs[_tokenId].proficiencyLevel;
        uint256 newLevel = calculateInitialProficiency(_score);
        uint256 verificationCount = skillNFTs[_tokenId].verificationCount;
        
        return (currentLevel * verificationCount + newLevel) / (verificationCount + 1);
    }
    
    // Override required functions
    function uri(uint256 _tokenId) public view override returns (string memory) {
        return string(abi.encodePacked(
            "https://api.proofofskill.swarm/metadata/",
            Strings.toString(_tokenId)
        ));
    }
}

library Strings {
    function toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }
        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buffer);
    }
}
