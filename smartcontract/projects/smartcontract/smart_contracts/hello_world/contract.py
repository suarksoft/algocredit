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
        
        # Yeni yatırımcı bilgileri
        self.registration_date = LocalState(UInt64)  # Kayıt tarihi (timestamp)
        self.total_invested = LocalState(UInt64)  # Toplam yatırım miktarı
        self.risk_preference = LocalState(UInt64)  # 1=Low, 2=Medium, 3=High
        self.min_investment = LocalState(UInt64)  # Minimum yatırım tutarı
        self.max_investment = LocalState(UInt64)  # Maksimum yatırım tutarı
        self.investor_status = LocalState(UInt64)  # 0=Inactive, 1=Active, 2=Suspended

    @abimethod()
    def get_platform_stats(self) -> arc4.Tuple[UInt64, UInt64, UInt64]:
        """Platform istatistiklerini döndür"""
        return arc4.Tuple((
            self.total_investors.value,
            self.total_startups.value, 
            self.total_funding_volume.value
        ))
    
    @abimethod()
    def register_or_update_investor(
        self, 
        initial_balance: UInt64,
        risk_preference: UInt64,
        min_investment: UInt64, 
        max_investment: UInt64
    ) -> String:
        """
        Yatırımcı kaydı veya güncelleme - Cüzdan adresi otomatik alınır
        Eğer zaten kayıtlıysa bilgileri günceller, değilse yeni kayıt oluşturur
        
        Args:
            initial_balance: İlk bakiye (microAlgo) - Sadece yeni kayıtta kullanılır
            risk_preference: Risk tercihi (1=Low, 2=Medium, 3=High)
            min_investment: Minimum yatırım tutarı
            max_investment: Maksimum yatırım tutarı
        """
        # Zaten kayıtlı mı kontrol et
        is_already_registered = self.user_type.value != UInt64(0)
        
        # Risk tercihi geçerli mi kontrol et
        assert risk_preference >= UInt64(1) and risk_preference <= UInt64(3), "Invalid risk preference"
        
        # Yatırım tutarları mantıklı mı kontrol et
        assert min_investment <= max_investment, "Min investment cannot be greater than max"
        assert min_investment > UInt64(0), "Min investment must be greater than 0"
        
        if is_already_registered:
            # Zaten kayıtlı - sadece güncellenebilir bilgileri güncelle
            assert self.user_type.value == UInt64(1), "User is not an investor"
            
            # Güncellenebilir bilgiler
            self.risk_preference.value = risk_preference
            self.min_investment.value = min_investment
            self.max_investment.value = max_investment
            # Bakiye ve diğer bilgiler değişmez
            
            return "Investor info updated successfully"
        else:
            # Yeni kayıt - tüm bilgileri kaydet
            self.user_type.value = UInt64(1)  # 1 = Investor
            self.investor_balance.value = initial_balance
            self.registration_date.value = UInt64(1)  # TODO: Gerçek timestamp eklenecek
            self.total_invested.value = UInt64(0)  # Başlangıçta 0
            self.risk_preference.value = risk_preference
            self.min_investment.value = min_investment
            self.max_investment.value = max_investment
            self.investor_status.value = UInt64(1)  # 1 = Active
            
            # Platform istatistiklerini güncelle (sadece yeni kayıtta)
            self.total_investors.value = self.total_investors.value + UInt64(1)
            
            return "Investor registered successfully"

    @abimethod()
    def check_user_status(self) -> arc4.Tuple[UInt64, String]:
        """
        Kullanıcının kayıt durumunu kontrol et
        Returns: (user_type, status_message)
        user_type: 0=Not registered, 1=Investor, 2=Startup
        """
        user_type = self.user_type.value
        
        if user_type == UInt64(0):
            return arc4.Tuple((user_type, "Not registered"))
        elif user_type == UInt64(1):
            return arc4.Tuple((user_type, "Registered as Investor"))
        elif user_type == UInt64(2):
            return arc4.Tuple((user_type, "Registered as Startup"))
        else:
            return arc4.Tuple((user_type, "Unknown user type"))

    @abimethod()
    def get_investor_info(self) -> arc4.Tuple[UInt64, UInt64, UInt64, UInt64, UInt64, UInt64]:
        """
        Yatırımcı bilgilerini getir
        Returns: (balance, total_invested, risk_preference, min_investment, max_investment, status)
        """
        assert self.user_type.value == UInt64(1), "Not an investor"
        
        return arc4.Tuple((
            self.investor_balance.value,
            self.total_invested.value,
            self.risk_preference.value,
            self.min_investment.value,
            self.max_investment.value,
            self.investor_status.value
        ))

    @abimethod()
    def hello(self, name: String) -> String:
        """Test için geçici - sonra kaldırılacak"""
        return "Hello from AlgoCredit, " + name
