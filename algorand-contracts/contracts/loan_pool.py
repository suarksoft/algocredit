"""
Corporate Treasury Marketplace Smart Contract
PyTeal implementation for connecting investors with startups
"""

from pyteal import *


def corporate_treasury_marketplace():
    """
    Corporate Treasury Marketplace smart contract
    Connects investors with startups for funding
    """
    
    # Global state keys
    admin_key = Bytes("admin")
    total_investors_key = Bytes("total_investors")
    total_startups_key = Bytes("total_startups")
    total_funding_key = Bytes("total_funding")
    platform_fee_rate_key = Bytes("platform_fee_rate")
    
    # Local state keys for investors
    investor_balance_key = Bytes("investor_balance")
    investor_yield_key = Bytes("investor_yield")
    investor_portfolio_key = Bytes("investor_portfolio")
    
    # Local state keys for startups
    startup_credit_score_key = Bytes("startup_credit_score")
    startup_funding_amount_key = Bytes("startup_funding_amount")
    startup_interest_rate_key = Bytes("startup_interest_rate")
    startup_funding_status_key = Bytes("startup_funding_status")  # 0=none, 1=seeking, 2=funded, 3=repaid
    
    # Application calls
    on_create = Seq([
        # Initialize global state
        App.globalPut(admin_key, Txn.sender()),
        App.globalPut(pool_balance_key, Int(0)),
        App.globalPut(total_loans_key, Int(0)),
        App.globalPut(total_repaid_key, Int(0)),
        App.globalPut(default_rate_key, Int(0)),
        App.globalPut(min_credit_score_key, Int(650)),  # Minimum credit score of 650
        Return(Int(1))
    ])
    
    # Add liquidity to the pool (lenders)
    on_add_liquidity = Seq([
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        Assert(Gtxn[0].amount() > Int(0)),
        
        # Update pool balance
        App.globalPut(
            pool_balance_key,
            App.globalGet(pool_balance_key) + Gtxn[0].amount()
        ),
        
        Return(Int(1))
    ])
    
    # Set credit score (only admin can call this initially)
    on_set_credit_score = Seq([
        # Verify admin
        Assert(Txn.sender() == App.globalGet(admin_key)),
        
        # Get credit score from application args
        credit_score := Btoi(Txn.application_args[1]),
        target_account := Txn.application_args[2],
        
        # Validate credit score range (300-850)
        Assert(credit_score >= Int(300)),
        Assert(credit_score <= Int(850)),
        
        # Set local state for target account
        App.localPut(target_account, credit_score_key, credit_score),
        
        Return(Int(1))
    ])
    
    # Issue loan based on credit score
    on_issue_loan = Seq([
        # Get user's credit score
        user_credit_score := App.localGet(Txn.sender(), credit_score_key),
        
        # Verify minimum credit score
        Assert(user_credit_score >= App.globalGet(min_credit_score_key)),
        
        # Verify user doesn't already have an active loan
        Assert(App.localGet(Txn.sender(), loan_status_key) == Int(0)),
        
        # Get requested loan amount from args
        requested_amount := Btoi(Txn.application_args[1]),
        loan_term_months := Btoi(Txn.application_args[2]),
        
        # Calculate maximum loan amount based on credit score
        # Formula: (credit_score - 300) * 1000 microAlgos
        max_loan_amount := (user_credit_score - Int(300)) * Int(1000),
        
        # Determine approved amount (minimum of requested and max allowed)
        approved_amount := If(
            requested_amount <= max_loan_amount,
            requested_amount,
            max_loan_amount
        ),
        
        # Verify pool has sufficient balance
        Assert(App.globalGet(pool_balance_key) >= approved_amount),
        
        # Calculate interest rate based on credit score
        # Higher credit score = lower interest rate
        # Formula: 15 - (credit_score - 300) / 100
        interest_rate := Int(15) - ((user_credit_score - Int(300)) / Int(100)),
        
        # Calculate due date (approximate - 30 days * months in seconds)
        due_date := Global.latest_timestamp() + (loan_term_months * Int(2592000)),
        
        # Update user's local state
        App.localPut(Txn.sender(), loan_amount_key, approved_amount),
        App.localPut(Txn.sender(), loan_due_date_key, due_date),
        App.localPut(Txn.sender(), interest_rate_key, interest_rate),
        App.localPut(Txn.sender(), loan_status_key, Int(1)),  # Active loan
        
        # Update global state
        App.globalPut(
            pool_balance_key,
            App.globalGet(pool_balance_key) - approved_amount
        ),
        App.globalPut(
            total_loans_key,
            App.globalGet(total_loans_key) + approved_amount
        ),
        
        # Send loan amount to borrower
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Txn.sender(),
            TxnField.amount: approved_amount,
            TxnField.note: Bytes("AlgoCredit Loan Disbursement")
        }),
        InnerTxnBuilder.Submit(),
        
        Return(Int(1))
    ])
    
    # Repay loan
    on_repay_loan = Seq([
        # Verify user has an active loan
        Assert(App.localGet(Txn.sender(), loan_status_key) == Int(1)),
        
        # Verify payment transaction
        Assert(Gtxn[0].type_enum() == TxnType.Payment),
        Assert(Gtxn[0].receiver() == Global.current_application_address()),
        
        loan_amount := App.localGet(Txn.sender(), loan_amount_key),
        interest_rate := App.localGet(Txn.sender(), interest_rate_key),
        
        # Calculate total amount due (simple interest)
        # For MVP, we'll use simple calculation: loan_amount * (1 + interest_rate/100)
        total_due := loan_amount + (loan_amount * interest_rate / Int(100)),
        
        # Check if payment covers the full amount
        If(Gtxn[0].amount() >= total_due).Then(
            Seq([
                # Mark loan as repaid
                App.localPut(Txn.sender(), loan_status_key, Int(2)),
                
                # Update global state
                App.globalPut(
                    pool_balance_key,
                    App.globalGet(pool_balance_key) + Gtxn[0].amount()
                ),
                App.globalPut(
                    total_repaid_key,
                    App.globalGet(total_repaid_key) + Gtxn[0].amount()
                ),
                
                Return(Int(1))
            ])
        ).Else(
            Return(Int(0))  # Partial payments not supported in MVP
        )
    ])
    
    # Get loan info
    on_get_loan_info = Seq([
        # Return loan information in logs (for frontend to read)
        Log(Concat(
            Bytes("loan_amount:"),
            Itob(App.localGet(Txn.sender(), loan_amount_key))
        )),
        Log(Concat(
            Bytes("loan_status:"),
            Itob(App.localGet(Txn.sender(), loan_status_key))
        )),
        Log(Concat(
            Bytes("interest_rate:"),
            Itob(App.localGet(Txn.sender(), interest_rate_key))
        )),
        Return(Int(1))
    ])
    
    # Main program logic
    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.application_args[0] == Bytes("add_liquidity"), on_add_liquidity],
        [Txn.application_args[0] == Bytes("set_credit_score"), on_set_credit_score],
        [Txn.application_args[0] == Bytes("issue_loan"), on_issue_loan],
        [Txn.application_args[0] == Bytes("repay_loan"), on_repay_loan],
        [Txn.application_args[0] == Bytes("get_loan_info"), on_get_loan_info],
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
    approval_program = loan_pool_contract()
    clear_program = clear_state_program()
    
    # Print TEAL code
    print("=== APPROVAL PROGRAM ===")
    print(compileTeal(approval_program, Mode.Application, version=8))
    print("\n=== CLEAR STATE PROGRAM ===")
    print(compileTeal(clear_program, Mode.Application, version=8))
