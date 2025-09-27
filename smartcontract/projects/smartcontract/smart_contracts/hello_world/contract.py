from algopy import ARC4Contract, String, UInt64, GlobalState, LocalState, arc4
from algopy.arc4 import abimethod


class CorporateTreasury(ARC4Contract):
    """
    Corporate Treasury Marketplace - AlgoCredit
    Yatırımcıları startup'larla buluşturan platform
    """
    
    def __init__(self) -> None:
        # Global state - Platform genel bilgileri
        self.total_investors = GlobalState(UInt64(0))
        self.total_startups = GlobalState(UInt64(0))
        self.total_funding_volume = GlobalState(UInt64(0))
        self.platform_fee_rate = GlobalState(UInt64(2))  # %2 platform ücreti
        
        # Local state - Kullanıcı bilgileri
        self.user_type = LocalState(UInt64)  # 1=investor, 2=startup
        self.investor_balance = LocalState(UInt64)
        self.startup_credit_score = LocalState(UInt64)
        self.funding_status = LocalState(UInt64)  # 0=none, 1=seeking, 2=funded

    @abimethod()
    def get_platform_stats(self) -> arc4.Tuple[UInt64, UInt64, UInt64]:
        """Platform istatistiklerini döndür"""
        return arc4.Tuple((
            self.total_investors.value,
            self.total_startups.value, 
            self.total_funding_volume.value
        ))
    
    @abimethod()
    def hello(self, name: String) -> String:
        """Test için geçici - sonra kaldırılacak"""
        return "Hello from AlgoCredit, " + name
