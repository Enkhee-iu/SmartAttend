// Database connection check script
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function checkDatabase() {
  console.log('🔍 Database Connection Check\n');
  
  try {
    // 1. Check environment variables
    console.log('1. Environment Variables:');
    const dbUrl = process.env.DATABASE_URL;
    const directUrl = process.env.DIRECT_URL;
    
    if (dbUrl) {
      // Hide password in output
      const maskedUrl = dbUrl.replace(/:[^:@]+@/, ':****@');
      console.log('   ✅ DATABASE_URL:', maskedUrl);
    } else {
      console.log('   ❌ DATABASE_URL: Not set');
    }
    
    if (directUrl) {
      const maskedUrl = directUrl.replace(/:[^:@]+@/, ':****@');
      console.log('   ✅ DIRECT_URL:', maskedUrl);
    } else {
      console.log('   ❌ DIRECT_URL: Not set');
    }
    
    console.log('\n2. Database Connection:');
    
    // 2. Test connection
    await prisma.$connect();
    console.log('   ✅ Connected to database successfully');
    
    // 3. Test query
    console.log('\n3. Database Query Test:');
    const userCount = await prisma.user.count();
    console.log(`   ✅ Users table exists (${userCount} users)`);
    
    const attendanceCount = await prisma.attendance.count();
    console.log(`   ✅ Attendances table exists (${attendanceCount} attendances)`);
    
    const sessionCount = await prisma.session.count();
    console.log(`   ✅ Sessions table exists (${sessionCount} sessions)`);
    
    // 4. Schema check
    console.log('\n4. Database Schema:');
    const tables = await prisma.$queryRaw`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `;
    
    console.log('   ✅ Tables found:');
    tables.forEach((table) => {
      console.log(`      - ${table.table_name}`);
    });
    
    console.log('\n✅ Database check completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Database check failed:');
    console.error('   Error:', error.message);
    
    if (error.code === 'P1001') {
      console.error('   💡 Cannot reach database server');
      console.error('   💡 Check your DATABASE_URL connection string');
    } else if (error.code === 'P1000') {
      console.error('   💡 Authentication failed');
      console.error('   💡 Check your database credentials');
    } else if (error.code === 'P1017') {
      console.error('   💡 Server closed the connection');
      console.error('   💡 Check your database server status');
    }
    
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

checkDatabase();
