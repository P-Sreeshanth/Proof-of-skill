"""
Economic Models Module
Sustainable value distribution and economic algorithms for Proof-of-Skill Swarm
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Any, Tuple


class ProofOfSkillEconomics:
    def __init__(self):
        self.ubc_percentage = 0.1  # 10% of value creation goes to Universal Basic Creativity
        self.reputation_weight = 0.3
        self.skill_weight = 0.4
        self.impact_weight = 0.3
        self.employer_subscription_fee = 0.05  # 5% of transaction value
        self.dao_treasury_fee = 0.02  # 2% goes to DAO treasury
        
    def skill_to_value_conversion(
        self, 
        skill_proof: Dict[str, Any], 
        reputation_score: float, 
        impact_metrics: float
    ) -> float:
        """
        Convert skill proof to economic value
        
        Args:
            skill_proof: Dictionary containing skill proof details
            reputation_score: User's reputation score (0-1)
            impact_metrics: Impact metrics score (0-1)
            
        Returns:
            Calculated value in tokens
        """
        # Calculate base skill value
        skill_value = self.calculate_skill_value(skill_proof)
        
        # Adjust based on reputation
        reputation_multiplier = 1 + (reputation_score * self.reputation_weight)
        
        # Adjust based on impact
        impact_multiplier = 1 + (impact_metrics * self.impact_weight)
        
        total_value = skill_value * reputation_multiplier * impact_multiplier
        
        return total_value
    
    def employer_access_pricing(
        self, 
        skill_nft: Dict[str, Any], 
        demand_level: float, 
        supply_level: float
    ) -> float:
        """
        Calculate pricing for employer access to skill proofs
        
        Args:
            skill_nft: Skill NFT metadata
            demand_level: Current demand level (0-1)
            supply_level: Current supply level (0-1)
            
        Returns:
            Access price in tokens
        """
        # Base price depends on skill level and verification count
        proficiency = skill_nft.get('proficiencyLevel', 5)
        verification_count = skill_nft.get('verificationCount', 1)
        
        base_price = proficiency * 10 * verification_count
        
        # Adjust based on supply and demand
        supply_demand_ratio = demand_level / max(supply_level, 0.01)
        price_multiplier = min(2.0, max(0.5, supply_demand_ratio))
        
        final_price = base_price * price_multiplier
        
        return final_price
    
    def revenue_distribution(
        self, 
        total_revenue: float, 
        contributors: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Distribute revenue among contributors
        
        Args:
            total_revenue: Total revenue to distribute
            contributors: List of contributor dictionaries with 'address' and 'weight'
            
        Returns:
            Dictionary mapping addresses to revenue shares
        """
        if not contributors:
            return {}
        
        # Calculate contributor shares
        total_weight = sum(contributor.get('weight', 1.0) for contributor in contributors)
        
        if total_weight == 0:
            return {contrib.get('address', ''): 0.0 for contrib in contributors}
        
        distributed_revenue = {}
        for contributor in contributors:
            address = contributor.get('address', '')
            weight = contributor.get('weight', 1.0)
            share_percentage = weight / total_weight
            distributed_revenue[address] = total_revenue * share_percentage
        
        return distributed_revenue
    
    def universal_basic_creativity(
        self, 
        total_value_created: float, 
        active_users: int
    ) -> float:
        """
        Calculate Universal Basic Creativity dividend per user
        
        Args:
            total_value_created: Total value created in the system
            active_users: Number of active users
            
        Returns:
            UBC dividend per user
        """
        if active_users == 0:
            return 0.0
        
        ubc_pool = total_value_created * self.ubc_percentage
        return ubc_pool / active_users
    
    def reputation_lending(
        self, 
        reputation_score: float, 
        requested_amount: float
    ) -> Dict[str, Any]:
        """
        Calculate lending terms based on reputation
        
        Args:
            reputation_score: User's reputation score (0-1)
            requested_amount: Requested loan amount
            
        Returns:
            Dictionary with lending terms or rejection
        """
        # Base interest rate decreases with higher reputation
        base_rate = 0.1  # 10% base interest rate
        reputation_discount = reputation_score * 0.08  # Up to 8% discount
        
        interest_rate = max(0.02, base_rate - reputation_discount)  # Minimum 2% interest
        
        # Maximum loan amount increases with reputation
        max_loan = 1000 * (1 + reputation_score)
        
        if requested_amount > max_loan:
            return {
                'approved': False,
                'max_amount': max_loan,
                'reason': 'Requested amount exceeds reputation-based limit',
                'recommendation': f'Maximum approved amount: {max_loan:.2f} tokens'
            }
        
        repayment_amount = requested_amount * (1 + interest_rate)
        
        return {
            'approved': True,
            'amount': requested_amount,
            'interest_rate': interest_rate,
            'repayment_amount': repayment_amount,
            'term_months': 12,
            'monthly_payment': repayment_amount / 12
        }
    
    def automated_treasury_management(
        self, 
        current_treasury: float, 
        value_creation_rate: float, 
        network_growth_rate: float
    ) -> Dict[str, Any]:
        """
        Automated treasury management for sustainable growth
        
        Args:
            current_treasury: Current treasury balance
            value_creation_rate: Rate of value creation
            network_growth_rate: Rate of network growth
            
        Returns:
            Optimal allocation dictionary
        """
        # Calculate optimal allocation between development, rewards, reserves, and UBC
        def objective(x):
            development, rewards, reserves, ubc_fund = x
            # Maximize sustainable growth
            growth = (
                development * 0.3 + 
                rewards * 0.3 + 
                reserves * 0.2 + 
                ubc_fund * 0.2
            )
            # Factor in value creation and network growth
            growth *= (1 + value_creation_rate) * (1 + network_growth_rate)
            return -growth  # Negative because we're minimizing
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: sum(x) - current_treasury},  # Allocate all funds
            {'type': 'ineq', 'fun': lambda x: x[0] - current_treasury * 0.2},  # Min 20% development
            {'type': 'ineq', 'fun': lambda x: x[1] - current_treasury * 0.3},  # Min 30% rewards
            {'type': 'ineq', 'fun': lambda x: x[2] - current_treasury * 0.1},  # Min 10% reserves
            {'type': 'ineq', 'fun': lambda x: x[3] - current_treasury * 0.1}   # Min 10% UBC
        ]
        
        # Bounds
        bounds = [
            (current_treasury * 0.2, current_treasury * 0.4),  # Development
            (current_treasury * 0.3, current_treasury * 0.5),  # Rewards
            (current_treasury * 0.1, current_treasury * 0.3),  # Reserves
            (current_treasury * 0.1, current_treasury * 0.3)   # UBC
        ]
        
        # Initial guess
        x0 = [
            current_treasury * 0.3, 
            current_treasury * 0.3, 
            current_treasury * 0.2, 
            current_treasury * 0.2
        ]
        
        # Optimize
        try:
            result = minimize(
                objective, 
                x0, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                development, rewards, reserves, ubc_fund = result.x
                return {
                    'success': True,
                    'allocations': {
                        'development': float(development),
                        'rewards': float(rewards),
                        'reserves': float(reserves),
                        'ubc_fund': float(ubc_fund)
                    },
                    'percentages': {
                        'development': float(development / current_treasury * 100),
                        'rewards': float(rewards / current_treasury * 100),
                        'reserves': float(reserves / current_treasury * 100),
                        'ubc_fund': float(ubc_fund / current_treasury * 100)
                    },
                    'expected_growth': float(-result.fun)
                }
            else:
                return {
                    'success': False,
                    'message': 'Optimization failed',
                    'reason': result.message
                }
        except Exception as e:
            return {
                'success': False,
                'message': 'Optimization error',
                'error': str(e)
            }
    
    def calculate_skill_value(self, skill_proof: Dict[str, Any]) -> float:
        """
        Calculate base value of skill based on proof complexity
        
        Args:
            skill_proof: Skill proof metadata
            
        Returns:
            Base skill value in tokens
        """
        # Extract proof characteristics
        difficulty = skill_proof.get('difficulty', 5)
        completion_time = skill_proof.get('completionTime', 3600)
        score = skill_proof.get('score', 50)
        
        # Base value calculation
        difficulty_multiplier = difficulty / 10
        time_factor = min(1.0, 3600 / max(completion_time, 60))  # Faster is better
        score_factor = score / 100
        
        base_value = 100 * difficulty_multiplier * time_factor * score_factor
        
        return max(base_value, 10)  # Minimum value
    
    def calculate_reputation_score(
        self, 
        verification_count: int,
        average_score: float,
        completion_rate: float,
        community_ratings: List[float]
    ) -> float:
        """
        Calculate user reputation score
        
        Args:
            verification_count: Number of verified proofs
            average_score: Average challenge score
            completion_rate: Challenge completion rate (0-1)
            community_ratings: List of community ratings (0-5)
            
        Returns:
            Reputation score (0-1)
        """
        # Weight different factors
        verification_factor = min(verification_count / 100, 1.0)  # Cap at 100 verifications
        score_factor = average_score / 100
        completion_factor = completion_rate
        
        if community_ratings:
            community_factor = np.mean(community_ratings) / 5.0
        else:
            community_factor = 0.5  # Neutral if no ratings
        
        reputation = (
            verification_factor * 0.3 +
            score_factor * 0.3 +
            completion_factor * 0.2 +
            community_factor * 0.2
        )
        
        return min(reputation, 1.0)
    
    def dynamic_pricing(
        self,
        base_price: float,
        market_conditions: Dict[str, float],
        time_of_day: int = 12
    ) -> float:
        """
        Calculate dynamic pricing based on market conditions
        
        Args:
            base_price: Base price for the service
            market_conditions: Dictionary with demand, supply, volatility
            time_of_day: Hour of day (0-23)
            
        Returns:
            Adjusted price
        """
        demand = market_conditions.get('demand', 0.5)
        supply = market_conditions.get('supply', 0.5)
        volatility = market_conditions.get('volatility', 0.1)
        
        # Supply-demand adjustment
        sd_ratio = demand / max(supply, 0.01)
        sd_multiplier = 0.5 + (sd_ratio * 0.5)  # Range: 0.5 to 1.5+
        
        # Time-of-day adjustment (peak hours cost more)
        if 9 <= time_of_day <= 17:  # Business hours
            time_multiplier = 1.1
        else:
            time_multiplier = 0.9
        
        # Volatility adjustment
        volatility_adjustment = 1.0 + (volatility * 0.2)
        
        adjusted_price = base_price * sd_multiplier * time_multiplier * volatility_adjustment
        
        return max(adjusted_price, base_price * 0.5)  # Floor at 50% of base


def test_economic_models():
    """Test function for economic models"""
    economics = ProofOfSkillEconomics()
    
    print("Testing Skill to Value Conversion:")
    skill_proof = {'difficulty': 7, 'completionTime': 1800, 'score': 85}
    value = economics.skill_to_value_conversion(skill_proof, 0.8, 0.7)
    print(f"  Calculated Value: {value:.2f} tokens")
    
    print("\nTesting Treasury Management:")
    treasury_result = economics.automated_treasury_management(10000, 0.05, 0.03)
    if treasury_result['success']:
        print("  Allocations:")
        for key, val in treasury_result['allocations'].items():
            print(f"    {key}: {val:.2f} tokens ({treasury_result['percentages'][key]:.1f}%)")
    
    print("\nTesting Reputation Lending:")
    lending_result = economics.reputation_lending(0.75, 5000)
    if lending_result['approved']:
        print(f"  Approved: {lending_result['amount']:.2f} tokens")
        print(f"  Interest Rate: {lending_result['interest_rate']*100:.2f}%")
        print(f"  Monthly Payment: {lending_result['monthly_payment']:.2f} tokens")
    
    print("\nTesting UBC Distribution:")
    ubc = economics.universal_basic_creativity(100000, 1000)
    print(f"  UBC per User: {ubc:.2f} tokens")


if __name__ == '__main__':
    test_economic_models()
