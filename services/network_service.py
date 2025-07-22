import ipaddress
import netifaces
import logging
from datetime import datetime
from typing import List, Dict, Any
from ping3 import ping

logger = logging.getLogger(__name__)

class NetworkService:
    def __init__(self):
        pass
    
    @staticmethod
    def validate_ip(ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    def detect_network_interfaces(self) -> List[Dict[str, Any]]:
        """Detect available network interfaces"""
        interfaces = []
        
        try:
            for interface_name in netifaces.interfaces():
                # Skip loopback interfaces
                if interface_name.startswith('lo'):
                    continue
                
                addresses = netifaces.ifaddresses(interface_name)
                
                # Get IPv4 addresses
                if netifaces.AF_INET in addresses:
                    for addr_info in addresses[netifaces.AF_INET]:
                        ip_address = addr_info.get('addr')
                        netmask = addr_info.get('netmask')
                        
                        if ip_address and netmask:
                            # Calculate subnet
                            try:
                                network = ipaddress.IPv4Network(f"{ip_address}/{netmask}", strict=False)
                                subnet = str(network.network_address) + '/' + str(network.prefixlen)
                                
                                interfaces.append({
                                    'name': interface_name,
                                    'ip_address': ip_address,
                                    'subnet': subnet,
                                    'netmask': netmask
                                })
                            except Exception as e:
                                logger.warning(f"Error processing interface {interface_name}: {str(e)}")
                                continue
        
        except Exception as e:
            logger.error(f"Error detecting network interfaces: {str(e)}")
        
        return interfaces
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Alias for detect_network_interfaces for backward compatibility"""
        return self.detect_network_interfaces()
    
    def ping_address(self, ip_address: str) -> Dict[str, Any]:
        """Ping a single IP address using ping3 library (ICMP only)"""
        result = {
            'ip_address': ip_address,
            'status': 'unknown',
            'response_time': None,
            'timestamp': datetime.utcnow(),
            'error_message': None
        }
        
        try:
            # Use ICMP ping only
            response_time = ping(ip_address, timeout=3, unit='ms')
            
            if response_time is not None:
                result['status'] = 'up'
                result['response_time'] = response_time
                logger.info(f"Successfully ICMP pinged {ip_address}: {result['status']}, {response_time}ms")
            else:
                result['status'] = 'down'
                logger.debug(f"Host {ip_address} is down (no ICMP response)")
                
        except Exception as e:
            logger.error(f"Error pinging {ip_address}: {str(e)}")
            result['status'] = 'error'
            result['error_message'] = str(e)
        
        return result
    
    def ping_subnet(self, subnet: str) -> List[Dict[str, Any]]:
        """Ping an entire subnet using ping3"""
        results = []
        
        try:
            # Parse subnet notation (e.g., 192.168.1.0/24)
            network = ipaddress.IPv4Network(subnet, strict=False)
            
            # Ping each host in the subnet
            for host_ip in network.hosts():
                ip_str = str(host_ip)
                result = self.ping_address(ip_str)
                results.append(result)
                
        except Exception as e:
            logger.error(f"Error pinging subnet {subnet}: {str(e)}")
            # Return error result for the subnet
            results.append({
                'ip_address': subnet,
                'status': 'error',
                'response_time': None,
                'timestamp': datetime.utcnow(),
                'error_message': str(e)
            })
        
        return results
    
    def group_consecutive_ips(self, ip_addresses: List[str]) -> List[Dict[str, Any]]:
        """Group consecutive IP addresses into subnets for efficient pinging"""
        if not ip_addresses:
            return []
        
        groups = []
        
        try:
            # Convert to IP objects and sort
            ip_objects = []
            for ip_str in ip_addresses:
                try:
                    ip_obj = ipaddress.IPv4Address(ip_str)
                    ip_objects.append((ip_obj, ip_str))
                except ValueError:
                    # Handle invalid IPs individually
                    groups.append({
                        'type': 'single',
                        'addresses': [ip_str],
                        'subnet': None
                    })
            
            # Sort by IP address
            ip_objects.sort(key=lambda x: x[0])
            
            # Group consecutive IPs
            if ip_objects:
                current_group = [ip_objects[0][1]]
                
                for i in range(1, len(ip_objects)):
                    current_ip = ip_objects[i][0]
                    previous_ip = ip_objects[i-1][0]
                    
                    # Check if IPs are consecutive
                    if int(current_ip) - int(previous_ip) == 1:
                        current_group.append(ip_objects[i][1])
                    else:
                        # Finalize current group
                        if len(current_group) > 1:
                            # Create subnet for consecutive IPs
                            try:
                                first_ip = ipaddress.IPv4Address(current_group[0])
                                last_ip = ipaddress.IPv4Address(current_group[-1])
                                
                                # Calculate appropriate subnet
                                subnet = self._calculate_subnet(first_ip, last_ip)
                                
                                groups.append({
                                    'type': 'subnet',
                                    'addresses': current_group,
                                    'subnet': subnet
                                })
                            except Exception as e:
                                logger.warning(f"Error creating subnet for {current_group}: {str(e)}")
                                # Fall back to individual IPs
                                for ip in current_group:
                                    groups.append({
                                        'type': 'single',
                                        'addresses': [ip],
                                        'subnet': None
                                    })
                        else:
                            # Single IP
                            groups.append({
                                'type': 'single',
                                'addresses': current_group,
                                'subnet': None
                            })
                        
                        # Start new group
                        current_group = [ip_objects[i][1]]
                
                # Handle the last group
                if len(current_group) > 1:
                    try:
                        first_ip = ipaddress.IPv4Address(current_group[0])
                        last_ip = ipaddress.IPv4Address(current_group[-1])
                        subnet = self._calculate_subnet(first_ip, last_ip)
                        
                        groups.append({
                            'type': 'subnet',
                            'addresses': current_group,
                            'subnet': subnet
                        })
                    except Exception as e:
                        logger.warning(f"Error creating subnet for {current_group}: {str(e)}")
                        for ip in current_group:
                            groups.append({
                                'type': 'single',
                                'addresses': [ip],
                                'subnet': None
                            })
                else:
                    groups.append({
                        'type': 'single',
                        'addresses': current_group,
                        'subnet': None
                    })
        
        except Exception as e:
            logger.error(f"Error grouping consecutive IPs: {str(e)}")
            # Fall back to individual IPs
            for ip in ip_addresses:
                groups.append({
                    'type': 'single',
                    'addresses': [ip],
                    'subnet': None
                })
        
        return groups
    
    def _calculate_subnet(self, first_ip: ipaddress.IPv4Address, last_ip: ipaddress.IPv4Address) -> str:
        """Calculate the smallest subnet that contains the range of IPs"""
        # Find the network that contains both IPs
        for prefix_len in range(32, 0, -1):
            try:
                network = ipaddress.IPv4Network(f"{first_ip}/{prefix_len}", strict=False)
                if last_ip in network:
                    return str(network)
            except Exception:
                continue
        
        # Fall back to /24 network of the first IP
        return str(ipaddress.IPv4Network(f"{first_ip}/24", strict=False))
    
    def ping_optimized(self, ip_addresses: List[str]) -> List[Dict[str, Any]]:
        """Ping IP addresses with optimization for consecutive addresses"""
        if not ip_addresses:
            return []
        
        all_results = []
        
        # Group consecutive IPs
        groups = self.group_consecutive_ips(ip_addresses)
        
        for group in groups:
            if group['type'] == 'subnet' and group['subnet']:
                # Ping the subnet
                subnet_results = self.ping_subnet(group['subnet'])
                
                # Filter results to only include IPs that were requested
                filtered_results = []
                for result in subnet_results:
                    if result['ip_address'] in group['addresses']:
                        filtered_results.append(result)
                
                # Add any missing IPs as down
                found_ips = {result['ip_address'] for result in filtered_results}
                for ip in group['addresses']:
                    if ip not in found_ips:
                        filtered_results.append({
                            'ip_address': ip,
                            'status': 'down',
                            'response_time': None,
                            'timestamp': datetime.utcnow(),
                            'error_message': None
                        })
                
                all_results.extend(filtered_results)
            else:
                # Ping individual IPs
                for ip in group['addresses']:
                    result = self.ping_address(ip)
                    all_results.append(result)
        
        return all_results
