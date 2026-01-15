#!/bin/bash
cd /opt/ri-scale-dashboard/frontend || exit
npm run build
rsync -av --delete dist/ /var/www/ri-scale-dashboard/
systemctl reload nginx
echo "Deployment complete!"