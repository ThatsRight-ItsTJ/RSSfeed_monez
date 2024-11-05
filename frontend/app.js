document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const hash = urlParams.get('hash');
    
    if (hash) {
        searchByHash(hash);
    }
    
    document.getElementById('contentLockerBackground').style.display = 'block';
    document.getElementById('contentLocker').style.display = 'block';
});

async function searchByHash(hash) {
    const contentDisplay = document.getElementById('contentInfo');
    const toolTitle = document.getElementById('tool-title');
    
    try {
        const response = await fetch(`/.netlify/functions/search?hash=${encodeURIComponent(hash)}`, {
            headers: {
                'X-API-Key': import.meta.env.VITE_OFFERS_API_KEY
            }
        });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch content');
        }
        
        toolTitle.textContent = `${data.content_class} Locked`;
        
        contentDisplay.innerHTML = `
            <div class="space-y-4">
                <h3 class="text-lg font-semibold">${escapeHtml(data.title)}</h3>
                ${data.image_url ? `<img src="${escapeHtml(data.image_url)}" alt="Content thumbnail" class="w-full rounded-lg">` : ''}
                <p class="text-gray-600">${escapeHtml(data.description)}</p>
                <div class="mt-4">
                    <button onclick="unlockContent('${escapeHtml(data.redirect_url)}')" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Unlock Content
                    </button>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error:', error);
        toolTitle.textContent = 'Content Not Found';
        contentDisplay.innerHTML = `
            <div class="text-center py-8">
                <div class="mb-4">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Content Not Available</h3>
                <p class="text-gray-500">The content you're looking for might have expired or is no longer available.</p>
                <p class="text-gray-500 mt-1">Please check back later or try a different link.</p>
            </div>
        `;
    }
}

function unlockContent(redirectUrl) {
    window.location.href = redirectUrl;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
