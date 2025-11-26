// api/order.js - GitHub Pages Function
export async function onRequestPost(context) {
    const { request } = context;
    
    try {
        const orderData = await request.json();
        
        // Триггерим GitHub Action через repository_dispatch
        const response = await fetch(`https://api.github.com/repos/ildar31/fixcad/dispatches`, {
            method: 'POST',
            headers: {
                'Authorization': `token ${context.env.GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                event_type: 'process_payment',
                client_payload: orderData
            })
        });

        if (response.ok) {
            return new Response(JSON.stringify({ success: true }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' }
            });
        } else {
            throw new Error('GitHub API error');
        }
    } catch (error) {
        return new Response(JSON.stringify({ error: 'Internal server error' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
