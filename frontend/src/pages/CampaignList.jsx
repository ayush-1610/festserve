import React, { useEffect, useState } from 'react';

function CampaignList() {
  const [campaigns, setCampaigns] = useState([]);

  useEffect(() => {
    async function load() {
      const res = await fetch('/api/campaigns', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (res.ok) {
        setCampaigns(await res.json());
      }
    }
    load();
  }, []);

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Campaigns</h1>
      <ul>
        {campaigns.map((c) => (
          <li key={c.campaign_id}>{c.product_id} - {c.units_allocated}</li>
        ))}
      </ul>
    </div>
  );
}

export default CampaignList;
