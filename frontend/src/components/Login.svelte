<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { api } from '../lib/api';
  import { login } from '../stores/auth';

  const dispatch = createEventDispatcher();

  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleSubmit() {
    loading = true;
    error = '';
    try {
      const data = await api.login(email, password);
      // Temporarily set token so getMe can use it
      login(data.access_token, { id: 0, email: '', is_active: false }); 
      const user = await api.getMe(); // Get user info after login
      login(data.access_token, user); // Update with real user info
      dispatch('success');
    } catch (e: any) {
      error = e.message || 'Login failed';
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex flex-col gap-4 p-6 bg-white rounded-lg shadow-md w-full max-w-md mx-auto">
  <h2 class="text-2xl font-bold text-center text-gray-800">Login</h2>
  
  {#if error}
    <div class="p-3 bg-red-100 text-red-700 rounded text-sm">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleSubmit} class="flex flex-col gap-4">
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input 
        type="email" 
        id="email" 
        bind:value={email} 
        required 
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
    
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
      <input 
        type="password" 
        id="password" 
        bind:value={password} 
        required 
        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <button 
      type="submit" 
      disabled={loading}
      class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
    >
      {loading ? 'Logging in...' : 'Login'}
    </button>
  </form>

  <div class="text-center text-sm text-gray-600">
    Don't have an account? 
    <button class="text-blue-600 hover:underline" on:click={() => dispatch('switch')}>Register</button>
  </div>
</div>
