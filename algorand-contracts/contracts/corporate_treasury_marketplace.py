"""
Corporate Treasury Marketplace Smart Contract
24-Hour Sprint Implementation
Yatırımcıları startup'larla buluşturan basit ama etkili platform
"""

from pyteal import *


def corporate_treasury_marketplace():
    """
    Corporate Treasury Marketplace - 24 saat sprint versiyonu
    Basit ama çalışan investor-startup matching sistemi
    """
    
    # Global state keys
    admin_key = Bytes("admin")
    total_investors_key = Bytes("total_investors")
    total_startups_key = Bytes("total_startups")
    total_funding_volume_key = Bytes("total_funding_volume")
    platform_fee_rate_key = Bytes("platform_fee_rate")  # 2% platform fee
    
    # Local state keys for investors
    investor_type_key = Bytes("investor_type")  # 1=investor, 2=startup
    investor_balance_key = Bytes("investor_balance")
    investor_yield_earned_key = Bytes("investor_yield_earned")
    investor_active_loans_key = Bytes("investor_active_loans")
    
    # Local state keys for startups
    startup_credit_score_key = Bytes("startup_credit_score")
    startup_requested_amount_key = Bytes("startup_requested_amount")
    startup_funded_amount_key = Bytes("startup_funded_amount")
    startup_interest_rate_key = Bytes("startup_interest_rate")
    startup_funding_status_key = Bytes("startup_funding_status")  # 0=none, 1=seeking, 2=funded, 3=repaid
    startup_investor_address_key = Bytes("startup_investor_address")
    
    # Application creation
    on_create = Seq([
        # Initialize global state
        App.globalPut(admin_key, Txn.sender()),
        App.globalPut(total_investors_key, Int(0)),
        App.globalPut(total_startups_key, Int(0)),
        App.globalPut(total_funding_volume_key, Int(0)),
        App.globalPut(platform_fee_rate_key, Int(2)),  # 2% platform fee
        Return(Int(1))
    ])
    
    # Register as investor - Yatırımcı kaydı
    on_register_investor = Seq([
        # Set user type as investor
        App.localPut(Txn.sender(), investor_type_key, Int(1)),
        App.localPut(Txn.sender(), investor_balance_key, Int(0)),
        App.localPut(Txn.sender(), investor_yield_earned_key, Int(0)),
        App.localPut(Txn.sender(), investor_active_loans_key, Int(0)),
        
        # Update global counter
        total_investors := App.globalGet(total_investors_key),
        App.globalPut(total_investors_key, total_investors + Int(1)),
        
        Return(Int(1))
    ])
    
    # Register as startup - Startup kaydı
    on_register_startup = Seq([
        # Get credit score from application args
        credit_score := Btoi(Txn.application_args[1]),
        
        # Validate credit score (300-850 range)
        Assert(credit_score >= Int(300)),
        Assert(credit_score <= Int(850)),
        
        # Set user type as startup
        App.localPut(Txn.sender(), investor_type_key, Int(2)),
        App.localPut(Txn.sender(), startup_credit_score_key, credit_score),
        App.localPut(Txn.sender(), startup_funding_status_key, Int(0)),
        
        # Update global counter
        total_startups := App.globalGet(total_startups_key),
        App.globalPut(total_startups_key, total_startups + Int(1)),
        
        Return(Int(1))
    ])
    
    # Investor deposits ALGO - Yatırımcı para yatırır
    on_investor_deposit = Seq([
        # Verify this is an investor
        user_type := App.localGet(Txn.sender(), investor_type_key),
        Assert(user_type == Int(1)),
        
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        Assert(Gtxn[0].amount() > Int(0)),
        
        # Update investor balance
        current_balance := App.localGet(Txn.sender(), investor_balance_key),
        new_balance := current_balance + Gtxn[0].amount(),
        App.localPut(Txn.sender(), investor_balance_key, new_balance),
        
        Return(Int(1))
    ])
    
    # Startup requests funding - Startup fon talep eder
    on_request_funding = Seq([
        # Verify this is a startup
        user_type := App.localGet(Txn.sender(), investor_type_key),
        Assert(user_type == Int(2)),
        
        # Get requested amount from args
        requested_amount := Btoi(Txn.application_args[1]),
        Assert(requested_amount > Int(0)),
        
        # Check startup doesn't have active funding
        current_status := App.localGet(Txn.sender(), startup_funding_status_key),
        Assert(current_status == Int(0)),
        
        # Calculate interest rate based on credit score
        credit_score := App.localGet(Txn.sender(), startup_credit_score_key),
        # Formula: 15% - (credit_score - 300) / 100 * 0.1
        # Higher credit score = lower interest rate
        interest_rate := Int(15) - ((credit_score - Int(300)) / Int(10)),
        
        # Update startup state
        App.localPut(Txn.sender(), startup_requested_amount_key, requested_amount),
        App.localPut(Txn.sender(), startup_interest_rate_key, interest_rate),
        App.localPut(Txn.sender(), startup_funding_status_key, Int(1)),  # Seeking funding
        
        Return(Int(1))
    ])
    
    # Investor funds startup - Yatırımcı startup'ı fonlar
    on_fund_startup = Seq([
        # Verify this is an investor
        user_type := App.localGet(Txn.sender(), investor_type_key),
        Assert(user_type == Int(1)),
        
        # Get startup address from args
        startup_address := Txn.application_args[1],
        
        # Verify startup is seeking funding
        startup_status := App.localGet(startup_address, startup_funding_status_key),
        Assert(startup_status == Int(1)),
        
        # Get funding details
        requested_amount := App.localGet(startup_address, startup_requested_amount_key),
        investor_balance := App.localGet(Txn.sender(), investor_balance_key),
        
        # Verify investor has sufficient balance
        Assert(investor_balance >= requested_amount),
        
        # Calculate platform fee (2%)
        platform_fee := requested_amount * App.globalGet(platform_fee_rate_key) / Int(100),
        net_amount := requested_amount - platform_fee,
        
        # Update investor balance
        new_investor_balance := investor_balance - requested_amount,
        App.localPut(Txn.sender(), investor_balance_key, new_investor_balance),
        
        # Update investor active loans
        active_loans := App.localGet(Txn.sender(), investor_active_loans_key),
        App.localPut(Txn.sender(), investor_active_loans_key, active_loans + Int(1)),
        
        # Update startup state
        App.localPut(startup_address, startup_funded_amount_key, requested_amount),
        App.localPut(startup_address, startup_funding_status_key, Int(2)),  # Funded
        App.localPut(startup_address, startup_investor_address_key, Txn.sender()),
        
        # Update global funding volume
        total_funding := App.globalGet(total_funding_volume_key),
        App.globalPut(total_funding_volume_key, total_funding + requested_amount),
        
        # Send funds to startup
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: startup_address,
            TxnField.amount: net_amount,
            TxnField.note: Bytes("Corporate Treasury Funding")
        }),
        InnerTxnBuilder.Submit(),
        
        Return(Int(1))
    ])
    
    # Startup repays loan - Startup krediyi geri öder
    on_repay_loan = Seq([
        # Verify this is a startup with active funding
        user_type := App.localGet(Txn.sender(), investor_type_key),
        Assert(user_type == Int(2)),
        
        funding_status := App.localGet(Txn.sender(), startup_funding_status_key),
        Assert(funding_status == Int(2)),
        
        # Get loan details
        funded_amount := App.localGet(Txn.sender(), startup_funded_amount_key),
        interest_rate := App.localGet(Txn.sender(), startup_interest_rate_key),
        investor_address := App.localGet(Txn.sender(), startup_investor_address_key),
        
        # Calculate total amount due (simple interest for demo)
        interest_amount := funded_amount * interest_rate / Int(100),
        total_due := funded_amount + interest_amount,
        
        # Verify payment covers full amount
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].amount() >= total_due),
        
        # Update startup status
        App.localPut(Txn.sender(), startup_funding_status_key, Int(3)),  # Repaid
        
        # Update investor yield
        current_yield := App.localGet(investor_address, investor_yield_earned_key),
        new_yield := current_yield + interest_amount,
        App.localPut(investor_address, investor_yield_earned_key, new_yield),
        
        # Update investor balance (return principal + interest)
        investor_balance := App.localGet(investor_address, investor_balance_key),
        new_balance := investor_balance + total_due,
        App.localPut(investor_address, investor_balance_key, new_balance),
        
        # Update active loans count
        active_loans := App.localGet(investor_address, investor_active_loans_key),
        App.localPut(investor_address, investor_active_loans_key, active_loans - Int(1)),
        
        Return(Int(1))
    ])
    
    # Get marketplace stats - Platform istatistikleri
    on_get_stats = Seq([
        total_investors := App.globalGet(total_investors_key),
        total_startups := App.globalGet(total_startups_key),
        total_funding := App.globalGet(total_funding_volume_key),
        
        Log(Concat(Bytes("total_investors:"), Itob(total_investors))),
        Log(Concat(Bytes("total_startups:"), Itob(total_startups))),
        Log(Concat(Bytes("total_funding:"), Itob(total_funding))),
        
        Return(Int(1))
    ])
    
    # Get user info - Kullanıcı bilgileri
    on_get_user_info = Seq([
        user_type := App.localGet(Txn.sender(), investor_type_key),
        
        If(user_type == Int(1)).Then(
            # Investor info
            Seq([
                balance := App.localGet(Txn.sender(), investor_balance_key),
                yield_earned := App.localGet(Txn.sender(), investor_yield_earned_key),
                active_loans := App.localGet(Txn.sender(), investor_active_loans_key),
                
                Log(Concat(Bytes("user_type:investor"))),
                Log(Concat(Bytes("balance:"), Itob(balance))),
                Log(Concat(Bytes("yield_earned:"), Itob(yield_earned))),
                Log(Concat(Bytes("active_loans:"), Itob(active_loans)))
            ])
        ).ElseIf(user_type == Int(2)).Then(
            # Startup info
            Seq([
                credit_score := App.localGet(Txn.sender(), startup_credit_score_key),
                requested_amount := App.localGet(Txn.sender(), startup_requested_amount_key),
                funded_amount := App.localGet(Txn.sender(), startup_funded_amount_key),
                funding_status := App.localGet(Txn.sender(), startup_funding_status_key),
                
                Log(Concat(Bytes("user_type:startup"))),
                Log(Concat(Bytes("credit_score:"), Itob(credit_score))),
                Log(Concat(Bytes("requested_amount:"), Itob(requested_amount))),
                Log(Concat(Bytes("funded_amount:"), Itob(funded_amount))),
                Log(Concat(Bytes("funding_status:"), Itob(funding_status)))
            ])
        ),
        
        Return(Int(1))
    ])
    
    # Main program logic
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("register_investor"), on_register_investor],
        [Txn.application_args[0] == Bytes("register_startup"), on_register_startup],
        [Txn.application_args[0] == Bytes("investor_deposit"), on_investor_deposit],
        [Txn.application_args[0] == Bytes("request_funding"), on_request_funding],
        [Txn.application_args[0] == Bytes("fund_startup"), on_fund_startup],
        [Txn.application_args[0] == Bytes("repay_loan"), on_repay_loan],
        [Txn.application_args[0] == Bytes("get_stats"), on_get_stats],
        [Txn.application_args[0] == Bytes("get_user_info"), on_get_user_info],
        [Int(1), Return(Int(0))]  # Default case
    )
    
    return program


def clear_state_program():
    """
    Clear state program - called when user opts out
    """
    return Return(Int(1))


if __name__ == "__main__":
    # Compile the contract
    approval_program = corporate_treasury_marketplace()
    clear_program = clear_state_program()
    
    # Print TEAL code
    print("=== CORPORATE TREASURY MARKETPLACE APPROVAL PROGRAM ===")
    print(compileTeal(approval_program, Mode.Application, version=8))
    print("\n=== CLEAR STATE PROGRAM ===")
    print(compileTeal(clear_program, Mode.Application, version=8))
