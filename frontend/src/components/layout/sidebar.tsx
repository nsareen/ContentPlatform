import Link from "next/link";
import { usePathname } from "next/navigation";

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  items: SidebarItem[];
}

export function Sidebar({ items }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className="w-64 h-full bg-white border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-xl font-semibold text-[#6D3BEB]">Genome.AI</h2>
        <p className="text-sm text-[#475569]">Content Platform</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {items.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-3 py-2 rounded-md text-sm ${
                isActive
                  ? "bg-[#F5F0FF] text-[#6D3BEB]"
                  : "text-[#475569] hover:bg-[#F8FAFC]"
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
