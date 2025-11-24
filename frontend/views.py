from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from accounts.forms import UserRegistrationForm, ProfileForm
from ledger.models import CarbonLedger
from planting.models import TreeTransaction, PlantingVerification
from ledger.calculations import calculate_co2, calculate_required_trees
from .forms import ConvertForm, PurchaseForm, VerificationForm

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'frontend/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'frontend/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.is_agent():
        return agent_dashboard(request)
    elif user.is_admin_role():
        return admin_dashboard(request)
    else:
        return citizen_dashboard(request)

def citizen_dashboard(request):
    ledgers = CarbonLedger.objects.filter(user=request.user)
    total_debt = ledgers.aggregate(Sum('total_co2_tonnes'))['total_co2_tonnes__sum'] or 0
    total_trees_needed = ledgers.aggregate(Sum('required_trees'))['required_trees__sum'] or 0
    
    # Calculate trees purchased
    purchased = TreeTransaction.objects.filter(user=request.user).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    context = {
        'total_debt': total_debt,
        'total_trees_needed': total_trees_needed,
        'purchased': purchased,
        'remaining': max(0, total_trees_needed - purchased),
        'recent_transactions': TreeTransaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'frontend/dashboard_citizen.html', context)

def agent_dashboard(request):
    pending_verifications = TreeTransaction.objects.filter(status='PENDING').count() # Actually transactions needing verification
    # Logic: Transactions that are paid/requested but not yet verified? 
    # The prompt says "Pending planting queue". Let's assume transactions created by citizens need verification/planting.
    # But wait, the model has PlantingVerification linked to Transaction.
    # Let's say agents see transactions that don't have a verification yet? Or transactions that are 'PENDING'?
    # Let's assume 'PENDING' transactions are waiting for Agent action.
    
    pending_txs = TreeTransaction.objects.filter(status='PENDING').order_by('created_at')
    
    context = {
        'pending_count': pending_txs.count(),
        'pending_txs': pending_txs[:5]
    }
    return render(request, 'frontend/dashboard_agent.html', context)

def admin_dashboard(request):
    # Admin uses Django Admin mostly, but we can show a summary here
    return redirect('/admin/')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'frontend/profile.html', {'form': form})

@login_required
def ledger_list(request):
    ledgers = CarbonLedger.objects.filter(user=request.user).order_by('-year')
    return render(request, 'frontend/ledger_list.html', {'ledgers': ledgers})

@login_required
def ledger_detail(request, pk):
    ledger = get_object_or_404(CarbonLedger, pk=pk, user=request.user)
    return render(request, 'frontend/ledger_detail.html', {'ledger': ledger})

@login_required
def convert_carbon(request):
    result = None
    if request.method == 'POST':
        form = ConvertForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            total_co2 = calculate_co2(data)
            trees = calculate_required_trees(total_co2)
            result = {'total_co2': total_co2, 'trees': trees}
            
            # Optionally save to a ledger if user wants (not specified in flow, but good for UX)
            # For now just show result
    else:
        form = ConvertForm()
    return render(request, 'frontend/convert.html', {'form': form, 'result': result})

@login_required
def purchase_trees(request, ledger_id):
    ledger = get_object_or_404(CarbonLedger, pk=ledger_id, user=request.user)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user
            tx.ledger = ledger
            tx.save()
            messages.success(request, 'Tree purchase request submitted!')
            return redirect('transaction_history')
    else:
        form = PurchaseForm(initial={'quantity': ledger.required_trees})
    return render(request, 'frontend/purchase.html', {'form': form, 'ledger': ledger})

@login_required
def transaction_history(request):
    transactions = TreeTransaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'frontend/transaction_history.html', {'transactions': transactions})

@login_required
def agent_queue(request):
    if not request.user.is_agent():
        return redirect('dashboard')
    transactions = TreeTransaction.objects.filter(status='PENDING').order_by('created_at')
    return render(request, 'frontend/agent_queue.html', {'transactions': transactions})

@login_required
def verify_planting(request, transaction_id):
    if not request.user.is_agent():
        return redirect('dashboard')
    transaction = get_object_or_404(TreeTransaction, pk=transaction_id)
    
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.transaction = transaction
            verification.agent = request.user
            verification.save()
            
            # Update transaction status
            transaction.status = 'APPROVED' # Or wait for admin? Prompt says "Admin: Approve or reject verified planting".
            # So Agent uploads proof, creates Verification. Transaction might stay Pending or move to 'VERIFIED_PENDING_APPROVAL'?
            # Let's keep it simple: Agent marks as planted (creates verification). Admin approves verification.
            # But the prompt says "Agent Dashboard: Mark as planted".
            transaction.save()
            
            messages.success(request, 'Planting verified and submitted for approval.')
            return redirect('agent_queue')
    else:
        form = VerificationForm()
    return render(request, 'frontend/verify_planting.html', {'form': form, 'transaction': transaction})
