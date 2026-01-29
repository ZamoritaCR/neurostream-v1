"""
Dopamine.watch Subscription Utilities
NEW FILE - doesn't replace anything
"""

def is_premium(supabase_client, user_id: str) -> bool:
    """Check if user has premium subscription"""
    try:
        result = supabase_client.table('subscriptions')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('plan_type', 'premium')\
            .eq('status', 'active')\
            .execute()
        return len(result.data) > 0
    except:
        return False


def get_daily_usage(supabase_client, user_id: str) -> dict:
    """Get user's usage for today"""
    from datetime import date
    try:
        result = supabase_client.table('daily_usage')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('date', str(date.today()))\
            .execute()

        if result.data:
            return result.data[0]

        # Create new record for today
        new_record = {
            'user_id': user_id,
            'date': str(date.today()),
            'recommendations_count': 0,
            'mr_dp_chats_count': 0,
            'quick_dope_hits_count': 0
        }
        supabase_client.table('daily_usage').insert(new_record).execute()
        return new_record
    except:
        return {'recommendations_count': 0, 'mr_dp_chats_count': 0, 'quick_dope_hits_count': 0}


def check_can_use(supabase_client, user_id: str, feature: str) -> tuple:
    """
    Check if user can use a feature.
    Returns: (can_use: bool, remaining: int, limit: int)
    """
    # Premium = unlimited
    if is_premium(supabase_client, user_id):
        return (True, 999, 999)

    usage = get_daily_usage(supabase_client, user_id)

    limits = {
        'recommendation': ('recommendations_count', 5),
        'mr_dp': ('mr_dp_chats_count', 10),
        'quick_dope': ('quick_dope_hits_count', 3)
    }

    if feature not in limits:
        return (True, 999, 999)

    field, limit = limits[feature]
    used = usage.get(field, 0)
    remaining = max(0, limit - used)

    return (remaining > 0, remaining, limit)


def increment_usage(supabase_client, user_id: str, feature: str):
    """Increment usage counter after feature use"""
    from datetime import date

    field_map = {
        'recommendation': 'recommendations_count',
        'mr_dp': 'mr_dp_chats_count',
        'quick_dope': 'quick_dope_hits_count'
    }

    if feature not in field_map:
        return

    field = field_map[feature]

    try:
        # Get current count
        result = supabase_client.table('daily_usage')\
            .select(field)\
            .eq('user_id', user_id)\
            .eq('date', str(date.today()))\
            .execute()

        if result.data:
            current = result.data[0].get(field, 0)
            supabase_client.table('daily_usage')\
                .update({field: current + 1})\
                .eq('user_id', user_id)\
                .eq('date', str(date.today()))\
                .execute()
        else:
            # Create new record
            supabase_client.table('daily_usage').insert({
                'user_id': user_id,
                'date': str(date.today()),
                field: 1
            }).execute()
    except Exception as e:
        print(f"Error incrementing usage: {e}")


def show_usage_sidebar(st, supabase_client, user_id: str):
    """
    Show usage stats in sidebar
    Call this in your main app's sidebar section
    """
    if is_premium(supabase_client, user_id):
        st.sidebar.success("Premium Member")
        return

    usage = get_daily_usage(supabase_client, user_id)

    st.sidebar.markdown("### Daily Usage")

    # Recommendations
    rec_used = usage.get('recommendations_count', 0)
    st.sidebar.progress(min(rec_used/5, 1.0), text=f"Recommendations: {rec_used}/5")

    # Mr.DP
    dp_used = usage.get('mr_dp_chats_count', 0)
    st.sidebar.progress(min(dp_used/10, 1.0), text=f"Mr.DP Chats: {dp_used}/10")

    # Quick Dope
    qd_used = usage.get('quick_dope_hits_count', 0)
    st.sidebar.progress(min(qd_used/3, 1.0), text=f"Quick Dope Hits: {qd_used}/3")

    st.sidebar.markdown("---")
    if st.sidebar.button("Go Premium - Unlimited", key="sidebar_premium"):
        st.session_state.show_premium_modal = True
