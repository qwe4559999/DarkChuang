<script lang="ts">
  import { onMount } from 'svelte';
  import * as ThreeDMol from '3dmol';

  export let sdf: string;
  export let style: 'stick' | 'sphere' | 'line' = 'stick';
  export let className = 'h-64';
  
  let container: HTMLElement;
  let viewer: any;

  onMount(() => {
    if (container && sdf) {
      initViewer();
    }
  });

  $: if (viewer && sdf) {
    updateModel();
  }

  function initViewer() {
    const config = { backgroundColor: 'white' };
    viewer = ThreeDMol.createViewer(container, config);
    updateModel();
  }

  function updateModel() {
    viewer.clear();
    viewer.addModel(sdf, "sdf");
    
    if (style === 'stick') {
        viewer.setStyle({}, { stick: {} });
    } else if (style === 'sphere') {
        viewer.setStyle({}, { sphere: {} });
    } else {
        viewer.setStyle({}, { line: {} });
    }
    
    viewer.zoomTo();
    viewer.render();
  }
  
  function setStyle(newStyle: 'stick' | 'sphere' | 'line') {
      style = newStyle;
      updateModel();
  }
</script>

<div class={`relative w-full ${className} bg-gray-50 rounded-lg border border-gray-200 overflow-hidden`}>
  <div bind:this={container} class="w-full h-full"></div>
  
  <div class="absolute bottom-2 right-2 flex gap-1 bg-white/80 p-1 rounded shadow-sm backdrop-blur-sm">
      <button 
          class="px-2 py-1 text-xs rounded {style === 'stick' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}"
          on:click={() => setStyle('stick')}
      >Stick</button>
      <button 
          class="px-2 py-1 text-xs rounded {style === 'sphere' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}"
          on:click={() => setStyle('sphere')}
      >Sphere</button>
      <button 
          class="px-2 py-1 text-xs rounded {style === 'line' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}"
          on:click={() => setStyle('line')}
      >Line</button>
  </div>
</div>